import sys

import pygame
import pygame_gui
from level_parser import load_image
from constants import *


def start_screen():  # экран старта с кнопочками, я писал с видеоуроков яндекса, сам не особо что помню куда и как
    try:
        pygame.display.set_caption("Start menu")
        size = wight, height = 800, 600
        screen = pygame.display.set_mode(size)
        manager = pygame_gui.UIManager(size)
        intro_text = [
            "Я дам вам",
            "игру про",
            "Олега Тинькофф",
        ]
        font = pygame.font.Font(None, 30)
        fon = pygame.transform.scale(load_image("fons/menu_fon.jpg"), (wight, height))
        screen.blit(fon, (0, 0))
        run = True
        start_button = pygame_gui.elements.UIButton(  # кнопка старта
            relative_rect=pygame.Rect((100, 400), (100, 50)),
            text="Start",
            manager=manager,
        )
        exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((100, 500), (100, 50)),
            text="Exit",  # кнопка выхода
            manager=manager,
        )
        clock1 = pygame.time.Clock()

        while run:
            time_delta1 = clock1.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame_gui.windows.UIConfirmationDialog(
                        rect=pygame.Rect((300, 200), (300, 200)),
                        manager=manager,  # диалоговое окно
                        window_title="Ало?",
                        action_long_desc="Куда собрался?",
                        action_short_name="Ок",
                        blocking=True,
                    )
                if event.type == pygame.USEREVENT:  # если почалось
                    if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                        pygame.quit()
                        sys.exit()  # sys.exit() для корректного завершения
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == start_button:
                            start_button.hide()
                            return 0
                    if event.ui_element == exit_button:
                        pygame.quit()
                        sys.exit()
                manager.process_events(event)
            manager.update(time_delta1)
            screen.blit(fon, (0, 0))
            text_coord = MENU_TEXT_START_Y
            for line in intro_text:
                string_rendered = font.render(line, 1, pygame.Color("black"))
                intro_rect = string_rendered.get_rect()
                text_coord += MENU_TEXT_SPACING
                intro_rect.top = text_coord
                # более точное центрирование текста
                intro_rect.centerx = MENU_WIDTH // 2
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)
            manager.draw_ui(screen)
            pygame.display.update()
    except Exception:
        sys.exit()


def end_screen():  # абсолютно то же самое, но буковки другие
    pygame.display.set_caption("Start menu")
    size = wight, height = 800, 600
    screen = pygame.display.set_mode(size)
    manager = pygame_gui.UIManager(size)
    intro_text = [
        "Конец",
        "игры про",
        "Олега Тинькофф",
    ]
    font = pygame.font.Font(None, 30)
    fon = pygame.transform.scale(load_image("fons/menu_fon.jpg"), (wight, height))
    screen.blit(fon, (0, 0))
    run = True
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((100, 400), (100, 50)), text="exit", manager=manager
    )
    clock1 = pygame.time.Clock()

    while run:
        time_delta1 = clock1.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    pygame.quit()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        start_button.hide()
                        sys.exit()
            manager.process_events(event)
        manager.update(time_delta1)
        screen.blit(fon, (0, 0))
        text_coord = 100
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color("black"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 60 - len(line) * 4
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        manager.draw_ui(screen)
        pygame.display.update()
