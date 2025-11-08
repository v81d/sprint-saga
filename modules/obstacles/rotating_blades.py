import random

from modules.media import Media


class RotatingBlade:
    def __init__(self, instance, screen_width, screen_height, max_blades=5):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        self.media = Media(self.instance, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.character_height = self.media.character[0].get_height()
        self.ground_height = self.media.ground.get_height()

        self.max_blades = max_blades
        self.blades = []

        self.player_collided = False

    def spawn_blade(self):
        if len(self.blades) < self.max_blades and random.randint(1, 2) == 1:
            blade = {
                "rotating_blade": self.media.load_rotating_blade(),
                "x_position": self.SCREEN_WIDTH + 128,
                "y_position": random.uniform(
                    self.SCREEN_HEIGHT
                    - self.ground_height
                    - self.character_height
                    - 160,
                    self.SCREEN_HEIGHT
                    - self.ground_height
                    - self.character_height
                    - 64,
                ),
                "rotation_degrees": 0,
                "rotation_speed": random.randint(2, 6),
                "on_screen": True,
            }
            self.blades.append(blade)

    def update_and_draw_blades(self, scroll_speed):
        for blade in self.blades[:]:
            if blade["on_screen"]:
                self.media.draw_rotating_blade(
                    blade["x_position"],
                    blade["y_position"],
                    blade["rotation_degrees"],
                    blade["rotating_blade"],
                )
                blade["x_position"] -= scroll_speed * 2.2
                blade["rotation_degrees"] += blade["rotation_speed"]

                if blade["x_position"] < -blade["rotating_blade"].get_width():
                    blade["on_screen"] = False
            else:
                self.blades.remove(blade)

    def check_collisions(self, character_y_position):
        character_image = self.media.character[0]
        character_rect = character_image.get_rect(
            topleft=(self.media.character_x_position, character_y_position)
        )

        for blade in self.blades:
            if blade["on_screen"]:
                blade_image = blade["rotating_blade"]
                blade_position = (
                    blade["x_position"] + blade_image.get_width() * 0.1,
                    blade["y_position"],
                )
                blade_radius = int(blade_image.get_width() * 0.9 / 2)

                character_center = character_rect.center
                distance = (
                    (character_center[0] - blade_position[0]) ** 2
                    + (character_center[1] - blade_position[1]) ** 2
                ) ** 0.5

                if (
                    distance
                    < blade_radius
                    + min(character_rect.width, character_rect.height) / 2
                ):
                    self.player_collided = True
