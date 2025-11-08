import os
import random

import pygame

import modules.player as player
from modules.media import Media


class Handlers:
    def __init__(self, instance, screen_width, screen_height, scroll):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.SCROLL_SPEED = 3

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.character_height = self.media.character[0].get_height()
        self.ground_height = self.media.ground.get_height()

        self.run_frame_index = 0
        self.run_animation_speed = 4

        self.GRAVITY = 0.6
        self.JUMP_STRENGTH = 8
        self.MAX_JUMP_DURATION = 16
        self.velocity_y = 0
        self.jumping = False
        self.was_jumping = False
        self.jump_frame_index = 0
        self.jump_frame_delay = 200
        self.jump_button_released = False
        self.jump_duration = 0

        self.attributes = player.load_attributes()
        self.score = 0
        self.score_increment = 0.1
        self.energy = 100
        self.energy_ratio = self.energy / 100
        self.energy_regenerating_mode = False

        self.current_time = pygame.time.get_ticks()
        self.scroll = scroll
        self.step_sound_delay = 300
        self.last_frame_update = 0

        self.music_folder = "./assets/soundtrack/game"
        self.previous_track = None

        self.step_sound = pygame.mixer.Sound("./assets/sfx/step.wav")
        self.land_sound = pygame.mixer.Sound("./assets/sfx/land.wav")
        self.jump_sound = pygame.mixer.Sound("./assets/sfx/jump.wav")
        self.coin_sound = pygame.mixer.Sound("./assets/sfx/coin_collect.wav")

    def play_random(self):
        songs = [
            song
            for song in os.listdir(self.music_folder)
            if song.endswith(".wav") or song.endswith(".mp3") or song.endswith(".ogg")
        ]
        if songs:
            song = random.choice(songs)
            while song == self.previous_track:
                song = random.choice(songs)
            self.previous_track = song
            pygame.mixer.music.load(os.path.join(self.music_folder, song))
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.play()
            self.fade_in_music()

    def fade_in_music(self, fade_duration=10000):
        self.fade_start_time = pygame.time.get_ticks()
        self.fade_duration = fade_duration
        self.fade_target_volume = 0.3
        self.fading_in = True

    def update_music(self):
        elapsed_time = self.current_time - self.fade_start_time
        if elapsed_time < self.fade_duration:
            current_volume = self.fade_target_volume * (
                elapsed_time / self.fade_duration
            )
            pygame.mixer.music.set_volume(current_volume)
        else:
            pygame.mixer.music.set_volume(self.fade_target_volume)
            self.fading_in = False

    def handle_music(self):
        if not pygame.mixer.music.get_busy() and random.randint(1, 720) == 1:
            self.play_random()
        if hasattr(self, "fading_in") and self.fading_in:
            self.update_music()

    def handle_mouse_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()

    def handle_controls(self, canceled=False):
        self.handle_mouse_events()
        keys_pressed = pygame.key.get_pressed()
        if (
            keys_pressed[pygame.K_SPACE]
            or keys_pressed[pygame.K_w]
            or keys_pressed[pygame.K_k]
            or keys_pressed[pygame.K_UP]
            or (self.mouse_click[0] and not canceled)
        ):
            self.jump()
        elif self.jumping:
            self.jump_button_released = True

        if (
            (
                keys_pressed[pygame.K_LSHIFT]
                or keys_pressed[pygame.K_d]
                or keys_pressed[pygame.K_l]
            )
            and self.energy > 0
            and not self.energy_regenerating_mode
        ):
            self.sprint(False)
        else:
            self.sprint(True)

    def jump(self):
        if not self.jumping:
            self.jump_sound.play()
            self.jumping = True
            self.jump_button_released = False
            self.jump_duration = 0
            self.velocity_y = -self.JUMP_STRENGTH
        elif (
            not self.jump_button_released
            and self.jump_duration < self.MAX_JUMP_DURATION
        ):
            self.jump_duration += 1
            self.velocity_y -= self.GRAVITY

    def sprint(self, reset):
        if reset:
            self.SCROLL_SPEED = 3
            self.run_animation_speed = 4
            self.jump_frame_delay = 200
            self.score_increment = 0.1
            self.step_sound_delay = 300
            if self.energy < 3:
                self.energy_regenerating_mode = True
            if self.energy < 100:
                self.energy = min(self.energy + 0.08, 100)
                if self.energy_regenerating_mode and self.energy > 14.4:
                    self.energy_regenerating_mode = False
        else:
            self.SCROLL_SPEED = 4.5
            self.run_animation_speed = 3
            self.jump_frame_delay = 150
            self.score_increment = 0.16
            self.step_sound_delay = 225
            self.energy = max(self.energy - 0.26, 0)
            self.energy_regenerating_mode = False

    def update_canvas(self):
        self.scroll += self.SCROLL_SPEED
        self.media.draw_background(self.scroll, self.instance)
        self.media.draw_ground(self.scroll, self.instance)

    def update_energy(self):
        self.energy_ratio = self.energy / 100
        energy_level = (
            "full"
            if 85.6 <= self.energy <= 100
            else (
                "high"
                if 67 <= self.energy < 85.6
                else (
                    "medium"
                    if 34 <= self.energy < 67
                    else "low"
                    if 14.4 < self.energy < 34
                    else "very_low"
                )
            )
        )
        self.media.draw_image(
            f"./assets/media/energy/{energy_level}.png", 24, 24, 24, 24
        )
        pygame.draw.rect(
            self.instance, (23, 51, 46), (65, 24, 179, 25), border_radius=4
        )
        pygame.draw.rect(
            self.instance,
            (35, 157, 127),
            (69, 28, 171 * self.energy_ratio, 17),
            border_radius=4,
        )
        pygame.draw.rect(
            self.instance, (37, 73, 66), (67, 26, 175, 21), 3, border_radius=4
        )

    def update_player(self):
        self.was_jumping = self.jumping

        if self.jumping:
            self.media.character_y_position = min(
                self.media.character_y_position + self.velocity_y,
                self.SCREEN_HEIGHT - self.ground_height - self.character_height,
            )
            self.velocity_y += self.GRAVITY
            if (
                self.media.character_y_position
                >= self.SCREEN_HEIGHT - self.ground_height - self.character_height
            ):
                if self.was_jumping:  # Player has landed
                    self.land_sound.play()
                self.jumping = False
                self.jump_button_released = False
                self.media.character_y_position = (
                    self.SCREEN_HEIGHT - self.ground_height - self.character_height
                )
                self.velocity_y = 0
            if self.current_time - self.last_frame_update >= self.jump_frame_delay:
                self.jump_frame_index = (self.jump_frame_index + 1) % len(
                    self.media.character_midair
                )
                self.last_frame_update = self.current_time
            self.media.draw_character_jump(self.velocity_y > 0, self.jump_frame_index)
        else:
            self.run_frame_index = (self.run_frame_index + 1) % (
                len(self.media.character) * self.run_animation_speed
            )
            self.media.draw_character(self.run_frame_index // self.run_animation_speed)
            if self.current_time - self.last_frame_update >= self.step_sound_delay:
                self.step_sound.play()
                self.last_frame_update = self.current_time

    def update_stats(self, score, coins):
        if self.score > self.attributes["personal_record"]:
            self.attributes["personal_record"] = int(score)
        self.media.draw_text(
            text=f"BEST {self.attributes['personal_record']:05}",
            y=24,
            size=24,
            outline_color=(37, 73, 66),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )
        self.media.draw_text(
            text=f"SCORE {int(score):05}",
            y=56,
            size=24,
            outline_color=(37, 73, 66),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )
        self.media.draw_text(
            text=f"COINS {int(coins):05}",
            y=88,
            size=24,
            outline_color=(37, 73, 66),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )
        self.score = score + self.score_increment
        self.coins = coins

    def save(self):
        if hasattr(self, "coins"):
            self.attributes["coins"] += int(self.coins)
        player.save_attributes(self.attributes)

    def reset(self):
        self.SCROLL_SPEED = 3

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.character_height = self.media.character[0].get_height()
        self.ground_height = self.media.ground.get_height()

        self.run_frame_index = 0
        self.run_animation_speed = 4

        self.GRAVITY = 0.6
        self.JUMP_STRENGTH = 8
        self.MAX_JUMP_DURATION = 16
        self.velocity_y = 0
        self.jumping = False
        self.was_jumping = False
        self.jump_frame_index = 0
        self.jump_frame_delay = 200
        self.jump_button_released = False
        self.jump_duration = 0

        self.attributes = player.load_attributes()
        self.score = 0
        self.score_increment = 0.1
        self.energy = 100
        self.energy_ratio = self.energy / 100
        self.energy_regenerating_mode = False

        self.current_time = pygame.time.get_ticks()
        self.step_sound_delay = 300
        self.last_frame_update = 0

        self.music_folder = "./assets/soundtrack/game"
        self.previous_track = None

        self.step_sound = pygame.mixer.Sound("./assets/sfx/step.wav")
        self.land_sound = pygame.mixer.Sound("./assets/sfx/land.wav")
        self.jump_sound = pygame.mixer.Sound("./assets/sfx/jump.wav")
        self.coin_sound = pygame.mixer.Sound("./assets/sfx/coin_collect.wav")
        self.step_sound.set_volume(0.3)
        self.land_sound.set_volume(0.5)
        self.jump_sound.set_volume(0.5)
        self.coin_sound.set_volume(0.6)
