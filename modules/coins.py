import random

import pygame

from modules.media import Media


class Coins:
    def __init__(self, instance, screen_width, screen_height):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.character_height = self.media.character[0].get_height()
        self.ground_height = self.media.ground.get_height()

        self.coin_on_screen = False
        self.coin_x_position = self.SCREEN_WIDTH + 100
        self.coin_y_position = 0
        self.coin_velocity = 10
        self.coin_gravity = 1
        self.coin_alpha = 255
        self.coin_frame_index = 0
        self.collected_coin_animation = False

        self.score_reward = 0
        self.coins = 0

        self.coin_sound = pygame.mixer.Sound("./assets/sfx/coin_collect.wav")

    def appear_coin(self):
        if random.randint(1, 8) == 1:
            self.coin_on_screen = True
            self.coin_x_position = self.SCREEN_WIDTH + self.media.coin[0].get_width()
            self.coin_y_position = random.uniform(
                self.SCREEN_HEIGHT - self.ground_height - self.character_height - 175,
                self.SCREEN_HEIGHT - self.ground_height - self.character_height - 100,
            )

    def redraw_coin(self, scroll_speed):
        if self.coin_on_screen:
            if self.coin_x_position > -self.media.coin[0].get_width():
                self.coin_frame_index = (self.coin_frame_index + 1) % len(
                    self.media.coin
                )
                self.media.draw_coin(
                    self.coin_frame_index,
                    self.coin_x_position,
                    self.coin_y_position,
                    self.coin_alpha,
                )
                self.coin_x_position -= scroll_speed * 2.2
            else:
                self.coin_x_position = self.SCREEN_WIDTH + 128
                self.score_reward = 0
                self.coin_on_screen = False

    def handle_coin_collision(
        self, run_frame_index, run_animation_speed, character_y_position
    ):
        character_image = self.media.character[
            (run_frame_index // run_animation_speed) % len(self.media.character)
        ]
        coin_image = (
            self.media.coin[self.coin_frame_index] if self.coin_on_screen else None
        )

        if coin_image:
            character_rect = character_image.get_rect(
                topleft=(self.media.character_x_position, character_y_position)
            )
            coin_position = (
                self.coin_x_position
                + coin_image.get_width() / 2
                + coin_image.get_width() * 0.175,
                self.coin_y_position + coin_image.get_height() / 2,
            )

            coin_radius = coin_image.get_width() / 2

            character_center = character_rect.center
            distance = (
                (character_center[0] - coin_position[0]) ** 2
                + (character_center[1] - coin_position[1]) ** 2
            ) ** 0.5

            if (
                distance
                < coin_radius + min(character_rect.width, character_rect.height) / 2
                and not self.collected_coin_animation
            ):
                self.score_reward = random.randint(50, 100)
                self.coins += 1
                self.collected_coin_animation = True
                self.coin_alpha = 255
                self.coin_sound.play()
            else:
                self.score_reward = 0

        if self.collected_coin_animation:
            self.coin_alpha = max(self.coin_alpha - 10, 0)

            self.coin_y_position -= self.coin_velocity
            self.coin_velocity -= self.coin_gravity

            if (
                self.coin_alpha <= 0
                and character_y_position
                >= self.SCREEN_HEIGHT - self.ground_height - self.character_height
            ):
                self.coin_on_screen = False
                self.collected_coin_animation = False
                self.coin_alpha = 255
                self.coin_velocity = 10
