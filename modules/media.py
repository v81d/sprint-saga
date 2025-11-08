import random

import pygame


class Media:
    def __init__(self, instance, screen_width, screen_height):
        self.instance = instance
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        self.backgrounds = self.load_backgrounds()
        self.ground = self.load_ground()
        self.ground_height = self.ground.get_height()
        self.character = self.load_character(46, 68)
        self.coin = self.load_coin()

        self.character_x_position = 100
        self.character_y_position = (
            self.SCREEN_HEIGHT - self.ground_height - self.character[0].get_height()
        )
        self.character_jump = pygame.transform.scale(
            pygame.image.load("./assets/media/character/jump.png").convert_alpha(),
            (46, 68),
        )
        self.character_midair = self.load_character_midair()
        self.character_landing = pygame.transform.scale(
            pygame.image.load("./assets/media/character/landing.png").convert_alpha(),
            (46, 68),
        )

    def load_backgrounds(self):
        layers = []
        for i in range(5):
            background = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/background/layer_{i}.png"
                ).convert_alpha(),
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            )
            layers.append(background)
        return layers

    def load_ground(self):
        return pygame.image.load("./assets/media/ground.png").convert_alpha()

    def load_character(self, width, height):
        frames = []
        for i in range(8):
            frame = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/character/run_frames/frame_{i}.png"
                ).convert_alpha(),
                (width, height),
            )
            frames.append(frame)
        return frames

    def load_character_midair(self):
        frames = []
        for i in range(2):
            frame = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/character/midair_frames/frame_{i}.png"
                ).convert_alpha(),
                (46, 68),
            )
            frames.append(frame)
        return frames

    def load_coin(self):
        frames = []
        for i in range(13):
            frame = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/coins/frame_{i}.png"
                ).convert_alpha(),
                (32, 32),
            )
            frames.append(frame)
        return frames

    def load_rotating_blade(self):
        return pygame.transform.scale(
            pygame.image.load(
                f"./assets/media/obstacles/rotating_blades/blade_{random.randint(0, 2)}.png"
            ).convert_alpha(),
            (64, 64),
        )

    def load_spikes(self):
        spikes = pygame.image.load(
            f"./assets/media/obstacles/spikes/spikes_{random.randint(0, 1)}.png"
        ).convert_alpha()

        w, h = spikes.get_size()

        return pygame.transform.scale(spikes, (w // 6, h // 6))

    def draw_background(self, scroll, surface):
        scroll_speed = 1
        for background in self.backgrounds:
            x_position = -(scroll * scroll_speed) % background.get_width()
            surface.blit(background, (x_position, 0))
            surface.blit(background, (x_position - background.get_width(), 0))
            scroll_speed += 0.2

    def draw_ground(self, scroll, surface):
        ground_width = self.ground.get_width()
        x_position = -(scroll * 2.2) % ground_width
        for i in range(-1, self.SCREEN_WIDTH // ground_width + 2):
            surface.blit(
                self.ground,
                (
                    x_position + i * ground_width,
                    self.SCREEN_HEIGHT - self.ground.get_height(),
                ),
            )

    def draw_character(self, frame_index):
        self.instance.blit(
            self.character[frame_index],
            (self.character_x_position, self.character_y_position),
        )

    def draw_character_jump(self, falling, frame_index):
        if (
            self.character_y_position
            >= self.SCREEN_HEIGHT
            - self.ground_height
            - self.character[0].get_height()
            - 80
        ):
            if not falling:
                self.instance.blit(
                    self.character_jump,
                    (self.character_x_position, self.character_y_position),
                )
            elif falling:
                self.instance.blit(
                    self.character_landing,
                    (self.character_x_position, self.character_y_position),
                )
        else:
            self.instance.blit(
                self.character_midair[frame_index],
                (self.character_x_position, self.character_y_position),
            )

    def draw_coin(self, frame_index, x, y=-32767, alpha=255):
        coin = self.coin[frame_index].copy()
        coin.set_alpha(alpha)

        if y == -32767:
            y = (
                self.SCREEN_HEIGHT
                - self.ground_height
                - self.coin[0].get_height()
                - 100
            )

        self.instance.blit(coin, (x, y))

    def draw_rotating_blade(self, x, y, rotation, rotating_blade):
        rotated_blade = pygame.transform.rotate(rotating_blade, rotation)

        blade_rect = rotated_blade.get_rect()
        blade_rect.center = (x, y)

        self.instance.blit(rotated_blade, blade_rect.topleft)

    def draw_spikes(self, x, y, spikes):
        spikes_rect = spikes.get_rect()
        spikes_rect.center = (x, y)

        self.instance.blit(spikes, spikes_rect.center)

    def draw_image(self, path, x, y, w, h, color=None):
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (w, h))

        if color:
            colored_image = (
                pygame.Surface(image.get_size()).convert_alpha(),
                (
                    w,
                    h,
                ),
            )
            colored_image.fill(color)
            colored_image.blit(image, (x, y), special_flags=pygame.BLEND_MULT)
        else:
            self.instance.blit(image, (x, y))

    def draw_text(
        self,
        text,
        y,
        x=None,
        size=28,
        color=(237, 255, 252),
        outline_color=None,
        font="./assets/glyphs/fonts/Monolith.ttf",
        alpha=255,
        centered_x=False,
    ):
        text = str(text)
        font = pygame.font.Font(font, size)

        text_surface = font.render(text, True, color)
        text_surface = text_surface.convert_alpha()

        text_surface.set_alpha(alpha)

        text_width = text_surface.get_width()

        if not x:
            x = self.SCREEN_WIDTH - text_width - size

        if centered_x:
            x = self.SCREEN_WIDTH / 2 - text_width / 2

        if outline_color:
            outline_surface = font.render(text, True, outline_color)
            outline_surface = outline_surface.convert_alpha()
            outline_surface.set_alpha(alpha)

            self.instance.blit(outline_surface, (x - 2, y))
            self.instance.blit(outline_surface, (x + 2, y))
            self.instance.blit(outline_surface, (x, y - 2))
            self.instance.blit(outline_surface, (x, y + 2))

        self.instance.blit(text_surface, (x, y))
