import sys
import os
import random
import pygame
import modules.player as player
from modules.game import Game
from modules.button import Button
from modules.media import Media
from modules.handlers import Handlers
from datetime import date, datetime


pygame.init()

FPS = 60
SCREEN_WIDTH = 860
SCREEN_HEIGHT = 440

instance = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(pygame.image.load("./assets/media/icon.ico"))
pygame.display.set_caption("Sprint Saga")

clock = pygame.time.Clock()
scroll = 0
SCROLL_SPEED = 0.2

media = Media(instance, SCREEN_WIDTH, SCREEN_HEIGHT)
handlers = Handlers(instance, SCREEN_WIDTH, SCREEN_HEIGHT, scroll)

background = pygame.Surface(instance.get_size())

YYYY = 2000

seasons = [
    ("winter", (date(YYYY, 1, 1), date(YYYY, 3, 20))),
    ("spring", (date(YYYY, 3, 21), date(YYYY, 6, 20))),
    ("summer", (date(YYYY, 6, 21), date(YYYY, 9, 22))),
    ("autumn", (date(YYYY, 9, 23), date(YYYY, 12, 20))),
    ("winter", (date(YYYY, 12, 21), date(YYYY, 12, 31))),
]

pygame.mixer.init()

music_folder = "./assets/soundtrack/menu"
previous_track = None

click_sound = pygame.mixer.Sound("./assets/sfx/click.wav")
click_sound.set_volume(0.5)


def season(now):
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=YYYY)
    return next(season for season, (start, end) in seasons if start <= now <= end)


def draw_canvas():
    global scroll

    scroll += SCROLL_SPEED
    media.draw_background(scroll, background)
    media.draw_ground(scroll, background)

    instance.blit(background, (0, 0))
    instance.blit(overlay, (0, 0))


def main_menu(instance):
    global attributes, fading_in, running, title, play, exit, overlay

    attributes = player.load_attributes()

    overlay = pygame.Surface(instance.get_size())
    overlay.fill((0, 0, 0))
    overlay.set_alpha(96)

    title = pygame.transform.scale(
        pygame.image.load(
            f"./assets/media/titles/title_{season(date.today())}.png"
        ).convert_alpha(),
        (320, 180),
    )
    play = Button(
        x=(SCREEN_WIDTH - 128) / 2,
        y=220,
        width=128,
        height=64,
        default="./assets/media/buttons/play/default.png",
        pressed="./assets/media/buttons/play/pressed.png",
    )
    exit = Button(
        x=(SCREEN_WIDTH - 128) / 2,
        y=SCREEN_HEIGHT - 140,
        width=128,
        height=64,
        default="./assets/media/buttons/exit/default.png",
        pressed="./assets/media/buttons/exit/pressed.png",
    )
    tutorial = Button(
        x=SCREEN_WIDTH - 204,
        y=60,
        width=32,
        height=32,
        default=f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/default.png",
        pressed=f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/pressed.png",
    )

    def play_random():
        global previous_track

        songs = [f for f in os.listdir(music_folder) if f.endswith((".wav"))]
        if songs:
            song = random.choice(songs)

            while song == previous_track:
                song = random.choice(songs)

            previous_track = song

            pygame.mixer.music.load(os.path.join(music_folder, song))
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.play()

            fade_in_music()

    def fade_in_music(duration=10000):
        global fade_start_time, fade_duration, fade_target_volume, fading_in

        fade_start_time = pygame.time.get_ticks()
        fade_duration = duration
        fade_target_volume = 0.16
        fading_in = True

    def update_music():
        global current_time, fade_start_time, fade_duration, fade_target_volume, fading_in

        current_time = pygame.time.get_ticks()

        elapsed_time = current_time - fade_start_time
        if elapsed_time < fade_duration:
            current_volume = fade_target_volume * (elapsed_time / fade_duration)
            pygame.mixer.music.set_volume(current_volume)
        else:
            pygame.mixer.music.set_volume(fade_target_volume)
            fading_in = False

    def start_game():
        global attributes

        pygame.mixer.music.stop()

        ui_alpha = 255
        overlay_alpha = 96
        credits_alpha = 64

        decrement = 2
        ratio = ui_alpha / decrement

        while ui_alpha > 0:
            ui_alpha = max(0, ui_alpha - decrement)
            overlay_alpha = max(0, overlay_alpha - 96 / ratio)
            credits_alpha = max(36, credits_alpha - 28 / ratio)

            title.set_alpha(ui_alpha)
            play.set_alpha(ui_alpha)
            exit.set_alpha(ui_alpha)
            tutorial.set_alpha(ui_alpha)
            overlay.set_alpha(overlay_alpha)

            instance.blit(background, (0, 0))
            instance.blit(overlay, (0, 0))
            instance.blit(title, ((SCREEN_WIDTH - 320) / 2, 48))

            play.draw(instance)
            exit.draw(instance)
            tutorial.draw(instance)

            media.draw_text(
                text="SHOW TUTORIAL",
                y=68,
                x=SCREEN_WIDTH - 163,
                size=18,
                color=(227, 206, 193),
                outline_color=(0, 0, 0),
                alpha=ui_alpha,
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"HIGH SCORE {attributes['personal_record']}",
                y=20,
                x=20,
                size=20,
                outline_color=(37, 73, 66),
                alpha=ui_alpha,
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"TOTAL COINS {attributes['coins']}",
                y=20,
                size=20,
                outline_color=(37, 73, 66),
                alpha=ui_alpha,
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"FPS {int(clock.get_fps())}",
                y=SCREEN_HEIGHT - 28,
                x=14,
                size=14,
                color=(237, 255, 252),
                alpha=credits_alpha,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )
            media.draw_text(
                text="Sprint Saga",
                y=SCREEN_HEIGHT - 28,
                size=14,
                color=(237, 255, 252),
                alpha=credits_alpha,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )

            pygame.display.flip()

        instance.fill((0, 0, 0))
        handlers.reset()
        result = Game(instance, handlers, scroll).main()

        if result is True:  # Player wants to return to menu
            attributes = player.load_attributes()

            ui_alpha = 255
            overlay_alpha = 96
            credits_alpha = 64

            tutorial.default = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/default.png"
                ).convert_alpha(),
                (tutorial.width, tutorial.height),
            )
            tutorial.pressed = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/pressed.png"
                ).convert_alpha(),
                (tutorial.width, tutorial.height),
            )

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            tutorial.update(mouse_pos, mouse_click)

            title.set_alpha(ui_alpha)
            play.set_alpha(ui_alpha)
            exit.set_alpha(ui_alpha)
            tutorial.set_alpha(ui_alpha)
            overlay.set_alpha(overlay_alpha)

            black_overlay = pygame.Surface(instance.get_size())
            black_overlay.fill((0, 0, 0))

            instance.blit(background, (0, 0))
            instance.blit(overlay, (0, 0))
            instance.blit(title, ((SCREEN_WIDTH - 320) / 2, 48))

            play.draw(instance)
            exit.draw(instance)
            tutorial.draw(instance)

            media.draw_text(
                text="SHOW TUTORIAL",
                y=68,
                x=SCREEN_WIDTH - 163,
                size=18,
                color=(227, 206, 193),
                outline_color=(0, 0, 0),
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"HIGH SCORE {attributes['personal_record']}",
                y=20,
                x=20,
                size=20,
                outline_color=(37, 73, 66),
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"TOTAL COINS {attributes['coins']}",
                y=20,
                size=20,
                outline_color=(37, 73, 66),
                font="./assets/glyphs/fonts/PeaberryMono.ttf",
            )
            media.draw_text(
                text=f"FPS {int(clock.get_fps())}",
                y=SCREEN_HEIGHT - 28,
                x=14,
                size=14,
                color=(237, 255, 252),
                alpha=64,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )
            media.draw_text(
                text="Sprint Saga",
                y=SCREEN_HEIGHT - 28,
                size=14,
                color=(237, 255, 252),
                alpha=64,
                font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
            )

            steps = 120
            for i in range(steps):
                draw_canvas()

                mouse_pos = pygame.mouse.get_pos()
                mouse_click = pygame.mouse.get_pressed()
                tutorial.update(mouse_pos, mouse_click)

                instance.blit(background, (0, 0))
                instance.blit(overlay, (0, 0))
                instance.blit(title, ((SCREEN_WIDTH - 320) / 2, 48))

                play.draw(instance)
                exit.draw(instance)
                tutorial.draw(instance)

                media.draw_text(
                    text="SHOW TUTORIAL",
                    y=68,
                    x=SCREEN_WIDTH - 163,
                    size=18,
                    color=(227, 206, 193),
                    outline_color=(0, 0, 0),
                    font="./assets/glyphs/fonts/PeaberryMono.ttf",
                )
                media.draw_text(
                    text=f"HIGH SCORE {attributes['personal_record']}",
                    y=20,
                    x=20,
                    size=20,
                    outline_color=(37, 73, 66),
                    font="./assets/glyphs/fonts/PeaberryMono.ttf",
                )
                media.draw_text(
                    text=f"TOTAL COINS {attributes['coins']}",
                    y=20,
                    size=20,
                    outline_color=(37, 73, 66),
                    font="./assets/glyphs/fonts/PeaberryMono.ttf",
                )
                media.draw_text(
                    text=f"FPS {int(clock.get_fps())}",
                    y=SCREEN_HEIGHT - 28,
                    x=14,
                    size=14,
                    color=(237, 255, 252),
                    alpha=64,
                    font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
                )
                media.draw_text(
                    text="Sprint Saga",
                    y=SCREEN_HEIGHT - 28,
                    size=14,
                    color=(237, 255, 252),
                    alpha=64,
                    font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
                )

                progress = (i / steps) ** 8
                overlay_height = int(SCREEN_HEIGHT * (1 - progress))

                if overlay_height > 0:
                    instance.blit(
                        black_overlay,
                        (0, 0),
                        (0, 0, SCREEN_WIDTH, overlay_height),
                    )

                pygame.display.flip()

            pygame.event.clear()
            return True

        return False

    while running:
        clock.tick(FPS)

        if not pygame.mixer.music.get_busy():
            play_random()
        if "fading_in" in globals() and fading_in:
            update_music()

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        play_update = play.update(mouse_pos, mouse_click)
        if play_update == "CLICKED":
            click_sound.play()
        elif play_update == "RELEASED":
            result = start_game()
            if not result:  # If player chose to quit
                running = False

        exit_update = exit.update(mouse_pos, mouse_click)
        if exit_update == "CLICKED":
            click_sound.play()
        elif exit_update == "RELEASED":
            running = False

        tutorial_update = tutorial.update(mouse_pos, mouse_click)
        if tutorial_update == "CLICKED":
            click_sound.play()
        elif tutorial_update == "RELEASED":
            handlers.attributes["tutorial"] = int(not handlers.attributes["tutorial"])
            tutorial.default = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/default.png"
                ).convert_alpha(),
                (tutorial.width, tutorial.height),
            )
            tutorial.pressed = pygame.transform.scale(
                pygame.image.load(
                    f"./assets/media/buttons/{'checked' if handlers.attributes['tutorial'] else 'unchecked'}/pressed.png"
                ).convert_alpha(),
                (tutorial.width, tutorial.height),
            )
            handlers.save()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False
                        case pygame.K_SPACE:
                            result = start_game()
                            if not result:  # If player chose to quit
                                running = False
                case pygame.QUIT:
                    running = False

        draw_canvas()

        instance.blit(title, ((SCREEN_WIDTH - 320) / 2, 48))
        play.draw(instance)
        exit.draw(instance)
        tutorial.draw(instance)

        media.draw_text(
            text="SHOW TUTORIAL",
            y=68,
            x=SCREEN_WIDTH - 163,
            size=18,
            color=(227, 206, 193),
            outline_color=(0, 0, 0),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )
        media.draw_text(
            text=f"HIGH SCORE {attributes['personal_record']}",
            y=20,
            x=20,
            size=20,
            outline_color=(37, 73, 66),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )
        media.draw_text(
            text=f"TOTAL COINS {attributes['coins']}",
            y=20,
            size=20,
            outline_color=(37, 73, 66),
            font="./assets/glyphs/fonts/PeaberryMono.ttf",
        )

        media.draw_text(
            text=f"FPS {int(clock.get_fps())}",
            y=SCREEN_HEIGHT - 28,
            x=14,
            size=14,
            color=(237, 255, 252),
            alpha=64,
            font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
        )
        media.draw_text(
            text="Sprint Saga",
            y=SCREEN_HEIGHT - 28,
            size=14,
            color=(237, 255, 252),
            alpha=64,
            font="./assets/glyphs/fonts/Jupiteroid/Jupiteroid-Bold.ttf",
        )

        pygame.display.flip()


if __name__ == "__main__":
    running = True
    while running:
        result = main_menu(instance)
        if not result:  # If player chose to quit
            running = False

    # Peacefully exit the program
    pygame.quit()
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit()
