import json
import random

import pygame


class DeathScreen:
    def __init__(self, instance, screen_width, screen_height, media, handlers):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.media = media
        self.handlers = handlers

        self.overlay = pygame.Surface(instance.get_size())
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(0)

        self.base_vignette = pygame.Surface(
            (screen_width * 2, screen_height * 2), pygame.SRCALPHA
        )
        self.base_vignette.fill((255, 0, 0))

        center_x, center_y = screen_width, screen_height
        for x in range(screen_width * 2):
            for y in range(screen_height * 2):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                alpha = int(min(216, distance / 4))
                pixel_color = (255, 0, 0, alpha)
                self.base_vignette.set_at((x, y), pixel_color)

        self.max_tilt_angle = 3
        self.tilt_speed = 0.02
        self.current_tilt = 0

        self.zoom_factor = 1.0
        self.max_zoom = 1.25
        self.zoom_speed = 0.002
        self.zoom_easing = 0

        self.max_diagonal = int(
            (screen_width * 1.25**2 + screen_height * 1.25**2) ** 0.5
        )
        self.rotation_surface = pygame.Surface(
            (self.max_diagonal, self.max_diagonal), pygame.SRCALPHA
        )

        self.large_font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 64)
        self.small_font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 24)

        self.death_text = self.large_font.render("YOU DIED!", True, (255, 0, 0))
        self.menu_text = self.small_font.render(
            "PRESS SPACE TO RETURN TO MENU", True, (148, 148, 148)
        )
        self.menu_text = self.small_font.render(
            "PRESS SPACE TO RETURN TO MENU", True, (148, 148, 148)
        )

        with open("./assets/json/death_tips.json", "r", encoding="utf-8") as data:
            self.tips = json.load(data)

    def display(
        self,
        background,
        score,
        coins,
        high_score,
        shake_duration=0,
        shake_intensity=0,
    ):
        clock = pygame.time.Clock()
        alpha = 0
        vignette_alpha = 216
        fade_speed = 1.2
        vignette_fade_speed = 0.1
        shake_frames = 0

        tip = random.choice(self.tips).replace("{$SCORE}", str(score))
        font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 24)
        tip_surface = font.render(tip, True, (232, 135, 132))
        tip_rect = tip_surface.get_rect(
            center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 40)
        )

        diagonal = int((self.SCREEN_WIDTH**2 + self.SCREEN_HEIGHT**2) ** 0.5)
        rotation_surface = pygame.Surface((diagonal, diagonal), pygame.SRCALPHA)

        while True:
            clock.tick(60)

            if self.current_tilt < self.max_tilt_angle:
                self.current_tilt = min(
                    self.current_tilt + self.tilt_speed, self.max_tilt_angle
                )

                progress = self.current_tilt / self.max_tilt_angle
                self.zoom_factor = 1.0 + (self.max_zoom - 1.0) * (
                    progress * progress * (3 - 2 * progress)
                )

            zoomed_width = max(
                int(self.SCREEN_WIDTH * self.zoom_factor), self.SCREEN_WIDTH
            )
            zoomed_height = max(
                int(self.SCREEN_HEIGHT * self.zoom_factor), self.SCREEN_HEIGHT
            )

            diagonal = int((zoomed_width**2 + zoomed_height**2) ** 0.5)
            rotation_surface = pygame.Surface((diagonal, diagonal), pygame.SRCALPHA)
            rotation_surface.fill((0, 0, 0, 0))

            dx = (diagonal - zoomed_width) / 2
            dy = (diagonal - zoomed_height) / 2

            offset = (0, 0)
            if shake_frames < shake_duration:
                offset = (
                    random.randint(-shake_intensity, shake_intensity),
                    random.randint(-shake_intensity, shake_intensity),
                )
                shake_frames += 1

            scaled_bg = pygame.transform.smoothscale(
                background, (zoomed_width, zoomed_height)
            )

            rotation_surface.blit(scaled_bg, (dx + offset[0], dy + offset[1]))

            scaled_vignette = pygame.transform.smoothscale(
                self.base_vignette,
                (
                    int(self.SCREEN_WIDTH * self.zoom_factor * 2),
                    int(self.SCREEN_HEIGHT * self.zoom_factor * 2),
                ),
            )

            vignette_x = (diagonal - scaled_vignette.get_width()) / 2
            vignette_y = (diagonal - scaled_vignette.get_height()) / 2

            scaled_vignette.set_alpha(int(vignette_alpha))
            rotation_surface.blit(scaled_vignette, (vignette_x, vignette_y))
            vignette_alpha = max(-0.5, vignette_alpha - vignette_fade_speed)

            if vignette_alpha <= 0:
                vignette_alpha = 0

            rotated = pygame.transform.rotate(rotation_surface, self.current_tilt)
            rotated_rect = rotated.get_rect(
                center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
            )

            self.instance.fill((0, 0, 0))
            self.instance.blit(rotated, rotated_rect)

            self.overlay.set_alpha(alpha)
            self.instance.blit(self.overlay, (0, 0))

            font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 64)
            text_surface = font.render("YOU DIED!", True, (255, 0, 0))
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(
                center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 95)
            )
            self.instance.blit(text_surface, text_rect)

            font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 20)
            attributes_surface = font.render(
                f"SCORE {str(score) + (' (PB)' if score >= high_score else '')}    COINS {coins}",
                True,
                (148, 148, 148),
            )
            attributes_rect = attributes_surface.get_rect(
                center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 40)
            )
            attributes_surface.set_alpha(alpha)
            self.instance.blit(attributes_surface, attributes_rect)

            tip_surface.set_alpha(alpha)
            self.instance.blit(tip_surface, tip_rect)

            font = pygame.font.Font("./assets/glyphs/fonts/PeaberryMono.ttf", 24)
            subtitle_surface = font.render(
                "CLICK OR PRESS SPACE TO RETURN TO MENU", True, (148, 148, 148)
            )
            subtitle_surface.set_alpha(alpha)
            subtitle_rect = subtitle_surface.get_rect(
                center=(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 95)
            )
            self.instance.blit(subtitle_surface, subtitle_rect)

            if alpha < 184:
                alpha = min(alpha + fade_speed, 184)

            self.media.draw_text(
                text=f"FPS {int(clock.get_fps())}",
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
                    return False
                elif (
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                    or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
                    and alpha >= 32
                ):
                    black_overlay = pygame.Surface(self.instance.get_size())
                    black_overlay.fill((0, 0, 0))

                    height = self.SCREEN_HEIGHT
                    steps = 60
                    for i in range(steps):
                        self.instance.fill((0, 0, 0))
                        self.instance.blit(rotated, rotated_rect)

                        self.overlay.set_alpha(alpha)
                        self.instance.blit(self.overlay, (0, 0))

                        text_surface.set_alpha(alpha)
                        self.instance.blit(text_surface, text_rect)
                        attributes_surface.set_alpha(alpha)
                        self.instance.blit(attributes_surface, attributes_rect)
                        tip_surface.set_alpha(alpha)
                        self.instance.blit(tip_surface, tip_rect)
                        subtitle_surface.set_alpha(alpha)
                        self.instance.blit(subtitle_surface, subtitle_rect)

                        self.media.draw_text(
                            text=f"FPS {int(clock.get_fps())}",
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

                        progress = (i / steps) ** 4
                        overlay_height = int(height * progress)

                        self.instance.blit(
                            black_overlay,
                            (0, self.SCREEN_HEIGHT - overlay_height),
                        )
                        pygame.display.flip()
                        pygame.time.delay(4)

                    pygame.event.clear()
                    return True

            pygame.display.flip()

        return False
