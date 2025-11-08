import random

import pygame

from modules.media import Media


class Spike:
    def __init__(self, instance, screen_width, screen_height, max_spikes=5):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.ground_height = self.media.ground.get_height()

        self.max_spikes = max_spikes
        self.spikes = []

        self.player_collided = False

    def spawn_spikes(self):
        if len(self.spikes) < self.max_spikes and random.randint(1, 4) in (
            1,
            2,
            3,
        ):
            spike = {
                "spike": self.media.load_spikes(),
                "x_position": self.SCREEN_WIDTH + 232,
                "y_position": self.SCREEN_HEIGHT
                - self.ground_height
                - self.media.load_spikes().get_height()
                + 8,
                "on_screen": True,
            }
            self.spikes.append(spike)

    def update_and_draw_spikes(self, scroll_speed):
        for spike in self.spikes[:]:
            spike["x_position"] -= scroll_speed * 2.2

            if spike["on_screen"]:
                self.media.draw_spikes(
                    spike["x_position"], spike["y_position"], spike["spike"]
                )

                if spike["x_position"] < -spike["spike"].get_width():
                    spike["on_screen"] = False

            if (
                not spike["on_screen"]
                and spike["x_position"] < -spike["spike"].get_width() * 2
            ):
                self.spikes.remove(spike)

    def check_collisions(self, character_y_position):
        character_image = self.media.character[0]
        character_rect = character_image.get_rect(
            topleft=(self.media.character_x_position, character_y_position)
        )

        for spike in self.spikes:
            if spike["on_screen"]:
                spike_image = spike["spike"]
                spike_center_position = (
                    spike["x_position"]
                    + spike_image.get_width() / 2
                    - spike_image.get_width() * 0.05,
                    spike["y_position"]
                    + spike_image.get_height() / 2
                    + spike_image.get_height() * 0.05,
                )
                scaled_width, scaled_height = (
                    spike_image.get_width() / 2,
                    spike_image.get_height() / 2,
                )
                spikes_rect = pygame.transform.scale(
                    spike_image, (scaled_width, scaled_height)
                ).get_rect(center=spike_center_position)

                if character_rect.colliderect(spikes_rect):
                    self.player_collided = True
