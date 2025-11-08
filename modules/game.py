import random
import pygame
import json
from modules.death import DeathScreen
from modules.obstacles.spikes import Spike
from modules.obstacles.rotating_blades import RotatingBlade
from modules.coins import Coins
from modules.button import Button
from modules.media import Media


class Game:
    def __init__(self, instance, handlers, scroll):
        self.instance = instance
        self.FPS = 60
        self.SCREEN_WIDTH = 860
        self.SCREEN_HEIGHT = 440

        self.clock = pygame.time.Clock()

        self.skip = Button(
            x=self.SCREEN_WIDTH - 50,
            y=280,
            width=40,
            height=40,
            default="./assets/media/buttons/skip/default.png",
            pressed="./assets/media/buttons/skip/pressed.png",
        )
        self.skip_update = None

        self.handlers = handlers
        self.handlers.scroll = scroll

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.coins = Coins(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.rotating_blades = RotatingBlade(
            self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT
        )
        self.spikes = Spike(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.tutorial_step_start_time = None
        self.tutorial_steps = None
        with open("./assets/json/tutorial_steps.json", "r") as data:
            tutorial_data = json.load(data)
            self.tutorial_steps = tutorial_data["steps"]
            self.tutorial_duration = tutorial_data["duration"]

        self.character_height = self.handlers.media.character[0].get_height()
        self.ground_height = self.media.ground.get_height()

        self.death_screen = DeathScreen(
            self.instance,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.media,
            self.handlers,
        )

        self.thunder_sound = pygame.mixer.Sound("./assets/sfx/thunder.wav")
        self.death_sound = pygame.mixer.Sound("./assets/sfx/death.wav")
        self.click_sound = pygame.mixer.Sound("./assets/sfx/click.wav")
        self.thunder_sound.set_volume(0.2)
        self.death_sound.set_volume(0.2)
        self.click_sound.set_volume(0.5)

    def handle_death(self):
        final_score = self.handlers.score + self.coins.score_reward

        pygame.mixer.music.stop()
        self.thunder_sound.play()
        self.death_sound.play()

        background = self.instance.copy()

        self.handlers.update_stats(final_score, self.coins.coins)
        self.handlers.save()

        result = self.death_screen.display(
            background,
            int(final_score),
            self.coins.coins,
            self.handlers.attributes["personal_record"],
            shake_duration=15,
            shake_intensity=5,
        )
        return result  # Return the result to main menu

    def display_tutorial(self, text, duration):
        current_time = pygame.time.get_ticks()
        if self.tutorial_step_start_time is None:
            self.tutorial_step_start_time = current_time

        elapsed_time = current_time - self.tutorial_step_start_time
        fade_duration = 1000

        if elapsed_time < duration:
            if elapsed_time < fade_duration:
                # Fade-in effect
                alpha = int((elapsed_time / fade_duration) * 255)
            elif elapsed_time > duration - fade_duration:
                # Fade-out effect
                alpha = int(((duration - elapsed_time) / fade_duration) * 255)
            else:
                alpha = 255

            alpha = max(0, min(255, alpha))

            surface = pygame.Surface((self.SCREEN_WIDTH, 60))
            surface.set_alpha(int(alpha * 0.5))
            surface.fill((0, 0, 0))
            self.instance.blit(surface, (0, 270))

            self.media.draw_text(
                text=f"{self.tutorial_step + 1} / {len(self.tutorial_steps)}",
                y=312,
                x=6,
                size=12,
                color=(128, 128, 128),
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-BoldItalic.ttf",
                alpha=alpha,
            )

            self.media.draw_text(
                text=text,
                y=293,
                size=20,
                color=(255, 255, 255),
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
                alpha=alpha,
                centered_x=True,
            )

            if alpha == 255:
                mouse_pos = pygame.mouse.get_pos()
                mouse_click = pygame.mouse.get_pressed()
                self.skip_update = self.skip.update(mouse_pos, mouse_click)
                if self.skip_update == "CLICKED":
                    self.click_sound.play()
                elif self.skip_update == "RELEASED":
                    self.tutorial_step_start_time = current_time - (
                        duration - fade_duration
                    )
                    return False

            self.skip.set_alpha(alpha)
            self.skip.draw(self.instance)

            return False
        else:
            self.tutorial_step_time = None
            self.tutorial_step_start_time = None
            return True

    def main(self):
        self.running = True
        self.start_time = pygame.time.get_ticks()
        self.alive = True
        self.coin_update_timer = 0
        self.rotating_blade_update_timer = 0
        self.spikes_update_timer = 0
        self.tutorial_step = 0
        self.tutorial_step_time = None

        pygame.event.clear()

        while self.running:
            self.clock.tick(self.FPS)

            self.handlers.current_time = pygame.time.get_ticks()

            canceled = (
                True
                if self.skip_update in ["CLICKED", "RELEASED", "HOVERED"]
                and self.handlers.attributes["tutorial"] == 1
                else False
            )

            self.handlers.handle_music()
            self.handlers.handle_controls(canceled)
            self.handlers.update_canvas()
            self.handlers.update_energy()
            self.handlers.update_player()

            if self.alive:
                if self.handlers.attributes["tutorial"] == 0:
                    self.handlers.update_stats(
                        self.handlers.score + self.coins.score_reward,
                        self.coins.coins,
                    )

                    self.coin_update_timer += 1
                    if (
                        self.coin_update_timer >= random.uniform(1, 2.4) * self.FPS
                        and not self.coins.coin_on_screen
                    ):
                        self.coins.appear_coin()

                        if self.coins.coin_on_screen:
                            coin_rect = pygame.Rect(
                                self.coins.coin_x_position,
                                self.coins.coin_y_position,
                                32,
                                32,
                            )

                            for blade in self.rotating_blades.blades:
                                if blade["on_screen"]:
                                    blade_rect = pygame.Rect(
                                        blade["x_position"],
                                        blade["y_position"],
                                        64,
                                        64,
                                    )
                                    if (
                                        abs(coin_rect.centerx - blade_rect.centerx)
                                        < 128
                                        and abs(coin_rect.centery - blade_rect.centery)
                                        < 128
                                    ):
                                        self.coins.coin_on_screen = False
                                        break

                            if self.coins.coin_on_screen:
                                for spike in self.spikes.spikes:
                                    if spike["on_screen"]:
                                        spike_rect = pygame.Rect(
                                            spike["x_position"],
                                            spike["y_position"],
                                            32,
                                            32,
                                        )
                                        if (
                                            abs(coin_rect.centerx - spike_rect.centerx)
                                            < 100
                                            and abs(
                                                coin_rect.centery - spike_rect.centery
                                            )
                                            < 100
                                        ):
                                            self.coins.coin_on_screen = False
                                            break

                        self.coin_update_timer = 0

                    self.rotating_blade_update_timer += 1
                    if (
                        self.rotating_blade_update_timer
                        >= random.uniform(0.8, 2.4) * self.FPS
                    ):
                        self.rotating_blades.spawn_blade()
                        self.rotating_blade_update_timer = 0

                    self.spikes_update_timer += 1
                    if self.spikes_update_timer >= random.uniform(0.6, 5.2) * self.FPS:
                        self.spikes.spawn_spikes()
                        self.spikes_update_timer = 0

                    self.coins.redraw_coin(self.handlers.SCROLL_SPEED)
                    self.coins.handle_coin_collision(
                        self.handlers.run_frame_index,
                        self.handlers.run_animation_speed,
                        self.handlers.media.character_y_position,
                    )
                    self.rotating_blades.update_and_draw_blades(
                        self.handlers.SCROLL_SPEED
                    )
                    self.rotating_blades.check_collisions(
                        self.handlers.media.character_y_position
                    )
                    self.spikes.check_collisions(
                        self.handlers.media.character_y_position
                    )
                    self.spikes.update_and_draw_spikes(self.handlers.SCROLL_SPEED)

                    if (
                        self.rotating_blades.player_collided
                        or self.spikes.player_collided
                    ):
                        self.handlers.update_stats(
                            self.handlers.score + self.coins.score_reward,
                            self.coins.coins,
                        )
                        self.alive = False
                        return self.handle_death()
                else:
                    self.handlers.update_stats(0, 0)

                    if pygame.time.get_ticks() - self.start_time >= 1000:
                        if self.tutorial_step < len(self.tutorial_steps):
                            if self.tutorial_step_time is None:
                                self.tutorial_step_time = pygame.time.get_ticks()

                            tutorial_done = self.display_tutorial(
                                self.tutorial_steps[self.tutorial_step],
                                self.tutorial_duration,
                            )

                            if tutorial_done:
                                self.tutorial_step += 1
                        else:
                            self.handlers.attributes["tutorial"] = 0
                            self.tutorial_step = None

            self.media.draw_text(
                text=f"FPS {int(self.clock.get_fps())}",
                y=self.SCREEN_HEIGHT - 28,
                x=14,
                size=14,
                color=(237, 255, 252),
                alpha=36,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )
            self.media.draw_text(
                text="Sprint Saga",
                y=self.SCREEN_HEIGHT - 28,
                size=14,
                color=(237, 255, 252),
                alpha=36,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False

            pygame.display.flip()

        return True
