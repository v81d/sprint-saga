import pygame


class Button:
    def __init__(self, x, y, width, height, default, pressed):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.default = pygame.transform.scale(
            pygame.image.load(default).convert_alpha(), (width, height)
        )
        self.pressed = pygame.transform.scale(
            pygame.image.load(pressed).convert_alpha(), (width, height)
        )

        self.current = self.default
        self.clicked = False
        self.just_released = False

        self.mask = pygame.mask.from_surface(self.default)

    def draw(self, screen):
        screen.blit(self.current, (self.x, self.y))

    def update(self, mouse_pos, mouse_click):
        mouse_x, mouse_y = mouse_pos

        if (
            self.x <= mouse_x < self.x + self.default.get_width()
            and self.y <= mouse_y < self.y + self.default.get_height()
        ):
            if mouse_click[0] == 1:
                if not self.clicked:
                    self.clicked = True
                    self.just_released = False
                    self.current = self.pressed
                    return "CLICKED"
                self.current = self.pressed
            else:
                if self.clicked:
                    self.just_released = True
                self.clicked = False
                self.current = self.default
                if self.just_released:
                    self.just_released = False
                    return "RELEASED"
            return "HOVERED"
        else:
            self.current = self.default
            self.clicked = False
            self.just_released = False

        return None  # Ensure a return value

    def set_alpha(self, alpha):
        self.default.set_alpha(alpha)
        self.pressed.set_alpha(alpha)
