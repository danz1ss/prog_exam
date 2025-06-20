import os
import pygame
import pygame_gui  # это надо для кнопочек и окон диалогов
import sys  # это вот так называемые библиотеки, я их использовал
from random import choice, randrange
from screens import end_screen, start_screen  # приколы из других py файлов
from classes_modules import *
from level_parser import parse_level
from constants import *


def update_collision():  # обрабатывает коллизию (ушло 4 дня)
    global move_left, move_right, jump_velocity, gravity_flag, running, background_y, background_x, jump_count  # да, да-да, да, не осуждайте
    x_direction = None  # так надо, чтоб потом проверять
    movement = move_left + move_right  # направление, куда идёт игрок
    player.rect.x += movement  # игрок идёт
    if movement != 0 and not gravity_flag:  # анимация падения
        player.update_run_animation()
    else:
        player.update_idle_animation()  # анимация спокойствия
    if movement > 0:  # если бежит вправо, то картинка вправо
        if player.orientation < 0:
            player.image = pygame.transform.flip(player.image, True, False)
            player.orientation = 1
    elif movement < 0:  # влево
        if player.orientation > 0:
            player.image = pygame.transform.flip(player.image, True, False)
            player.orientation = -1
    if objects:  # проход по объектам и проверка коллизии с ними
        for game_object in objects:
            if player.mask.overlap(
                game_object.mask,  # если касается объекта, то идёт проверка
                (
                    game_object.rect.x - player.rect.x,
                    game_object.rect.y - player.rect.y,
                ),
            ):
                if isinstance(game_object, Wall):  # в стену не даст войти
                    player.rect.x -= movement
                elif isinstance(game_object, Land):  # сбоку в платформы не залезть
                    if player.rect.y + player.rect.height > game_object.rect.y + 1:
                        player.rect.x -= movement
                elif isinstance(game_object, Portal):  # коллизия с порталом
                    for portal in objects:
                        if isinstance(portal, Portal):  # поиск сопряжённого портала
                            if (
                                game_object.target_portal_id == portal.portal_id
                            ):  # проверка id портала
                                if (
                                    portal.portal_direction == "right"
                                ):  # игрока выкидывает чуть дальше влево или вправо, чтобы было получше
                                    if player.mask.overlap(
                                        game_object.mask,
                                        (
                                            game_object.rect.x - player.rect.x - 30,
                                            game_object.rect.y - player.rect.y,
                                        ),
                                    ):
                                        x_direction = 70  # вправо на 70+
                                else:
                                    if player.mask.overlap(
                                        game_object.mask,
                                        (
                                            game_object.rect.x - player.rect.x + 30,
                                            game_object.rect.y - player.rect.y,
                                        ),
                                    ):
                                        x_direction = -70  # влево на 70+
                                if (
                                    x_direction
                                ):  # если мы провели предыдущие проверки, то должно быть
                                    player_x, player_y = (
                                        portal.rect.x - player.rect.x + x_direction,
                                        player.rect.y - portal.rect.y,
                                    )  # координаты, куда нужно всё переместить
                                    for obj in objects:  # перенос и понеслось
                                        obj.rect.x = obj.rect.x - player_x
                                        obj.rect.y = (
                                            obj.rect.y + player_y - player.rect.height
                                        )
                                    for obj in player_objects:
                                        obj.rect.x = obj.rect.x - player_x
                                        obj.rect.y = (
                                            obj.rect.y + player_y - player.rect.height
                                        )
                                    exit_.rect.x = exit_.rect.x - player_x
                                    exit_.rect.y = (
                                        exit_.rect.y + player_y - player.rect.height
                                    )
                                    player_x //= 0.85  # вот чтобы паралакс оставался
                                    background_x += player_x
                                    portal.portal_sound.play()  # звук портала
                                    break
    if (
        (exit_.rect.x + 25 <= player.rect.x <= exit_.rect.x + exit_.rect.width)
        and (  # если игрок зашёл в зону выхода
            exit_.rect.x
            <= player.rect.x + player.rect.width
            <= exit_.rect.x + exit_.rect.width - 25
        )
    ) and (exit_.rect.y < player.rect.y < exit_.rect.y + exit_.rect.height):
        if all(exit_.exit_conditions):  # если все условия выполнены
            running = False
    player.rect.y += jump_velocity  # после огромного блока сверху, можно начать просчитывать передвижение по y
    if objects:
        for game_object in objects:
            if isinstance(
                game_object, Land
            ):  # вот чтобы фокусы Коперфилда не происходили очень сложно и мутурно считаем где игрок, куда подвинуть
                if player.mask.overlap(
                    game_object.mask,
                    (
                        game_object.rect.x - player.rect.x,
                        game_object.rect.y - player.rect.y - 2,
                    ),
                ):
                    if (
                        game_object.rect.y
                        <= player.rect.y
                        <= game_object.rect.y + game_object.rect.height
                    ):
                        player.rect.y = game_object.rect.y + game_object.rect.height
                        jump_velocity += 3.5  # чтобы игрок чуть-чуть завис вверху у платформы, иначе будет выглядеть так, что игрок вообще не прыгнул
                    elif (
                        player.rect.y + player.rect.height > game_object.rect.y + 1
                    ):  # если игрок стоит на поверхности отключаем гравитацию
                        player.rect.y = game_object.rect.y - player.rect.height
                    gravity_flag = False
                    break
        else:  # если там не отключилась гравитация, то она действует
            gravity_flag = True
            player.rect.y += GRAVITY
            player.update_fall_animation()  # анимация падения


def object_update():  # передвижения объектов, чтобы был эффект камеры в центре
    global background_x, background_y, exit_
    if (
        player.rect.x + 1 <= camera_rect.x
    ):  # игрок не может выйти за границу камеры на экране
        player.rect.x = camera_rect.x
        background_x += 2  # фон двигаем чуть помедленее, типа паралакс и фон далеко
        if background_x >= 600:  # если фон улетел в тартарары, возвращаем на место
            background_x = 0
        for game_object in objects:  # двигаем все платформы и стенки и т.д.
            game_object.rect.x += 7
        for player_object in player_objects:
            player_object.rect.x += 7
        exit_.rect.x += 7

    elif player.rect.width + player.rect.x - 1 >= camera_rect.width + camera_rect.x:
        player.rect.x = (
            camera_rect.x + camera_rect.width - player.rect.width
        )  # то же самое, что выше, но для правой границы камеры
        background_x -= 2
        if background_x <= -600:
            background_x = 0
        for game_object in objects:
            game_object.rect.x -= 7
        for player_object in player_objects:
            player_object.rect.x -= 7
        exit_.rect.x -= 7

    if (
        player.rect.y + 1 <= camera_rect.y
    ):  # тут уже просчёт по у, но порталы не очень дружат с паралаксом по вертикали, по этому здесь мы фон не двигаем
        player.rect.y = camera_rect.y
        for game_object in objects:
            game_object.rect.y += 7
        for player_object in player_objects:
            player_object.rect.y += 7
        exit_.rect.y += 7

    elif (
        player.rect.height + player.rect.y - 1 >= camera_rect.height + camera_rect.y
    ):  # нижняя граница камеры
        player.rect.y = camera_rect.y + camera_rect.height - player.rect.height
        for game_object in objects:
            game_object.rect.y -= 7
        for player_object in player_objects:
            player_object.rect.y -= 7
        exit_.rect.y -= 7


def draw_jump_counter(window, jump_count):
    """Отрисовывает счётчик прыжков в правом верхнем углу экрана"""
    font = pygame.font.Font(None, 36)  # размер шрифта
    text_color = (255, 255, 255)  # белый цвет
    counter_text = f"Прыжки: {jump_count}"
    text_surface = font.render(counter_text, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.topright = (590, 10)  # позиция в правом верхнем углу
    window.blit(text_surface, text_rect)


if __name__ == "__main__":
    pygame.init()  # инициализация всего

    start_screen()
    pygame.display.set_caption("Game")
    size = width, height = 600, 600
    main_window = pygame.display.set_mode(size)
    load_screen = pygame.transform.smoothscale(
        load_image("fons/load_screen.png"), (600, 600)
    )  # подгрузка экрана загрузки, чтоб не делать это каждый раз
    oleg = pygame.mixer.Sound(
        "../assets/sounds/lever_sound.mp3"
    )  # подгружаю этот звук, просто чтоб у меня был уже готовый объект для дальнейшего
    clock_delta = pygame.time.Clock()
    clock = pygame.time.Clock()

    gravity_flag = True
    manager = pygame_gui.UIManager(size)  # ui элементы вкл.
    for level in range(
        1, len(os.listdir("../assets/levels")) + 1
    ):  # из txt файла подгружаем уровени
        player, level_background, level_sky, objects, player_objects, music, exit_ = (
            parse_level(f"{level}_level")
        )  # из функции отбираем все объеты
        indicator = Indicator(
            main_window, exit_
        )  # рисуем кружочки в зависимости от кол-ва условий
        background = pygame.transform.smoothscale(
            load_image(f"fons/{level_background}"), (width, height)
        )  # растягиваем задник
        background_2 = pygame.transform.smoothscale(
            load_image(f"fons/{level_sky}"), (5000, 3000)
        )

        background_x, background_y = 0, 0  # координаты фона
        pygame.mixer.music.load(
            f"../assets/sounds/fon_music/{music}"
        )  # загружаем и запускаем музыку с уровня
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
        camera_rect = pygame.Rect(
            (300 - 75, 300 - 40), (150, 80)
        )  # определяем грани камеры
        running = True
        jump_velocity = 0
        jump_count = 0  # счётчик прыжков
        while running:
            # запихиваем задник
            main_window.blit(background, (background_x, background_y))
            main_window.blit(background, (background_x + 600, background_y))
            main_window.blit(background, (background_x - 600, background_y))
            main_window.blit(background_2, (-2500, background_y - 3000))
            keys_pressed = pygame.key.get_pressed()  # смотрим на нажатые клавиши
            time_delta = clock_delta.tick(60) / 1000
            for (
                event
            ) in (
                pygame.event.get()
            ):  # если игрок нажал Х, аккуратно спрашиваем, точно ли он выйти хотел
                if event.type == pygame.QUIT:
                    confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                        rect=pygame.Rect((150, 200), (300, 200)),
                        manager=manager,
                        window_title="Ало?",
                        action_long_desc="Куда собрался?",
                        action_short_name="Ок",
                        blocking=True,
                    )

                if event.type == pygame.KEYDOWN:  # проверка клавиш
                    if (
                        event.key == pygame.K_w or event.key == pygame.K_SPACE
                    ):  # на пробел прыжок, но только если игрок не пересекается ни с чем
                        if any(
                            player.mask.overlap(
                                land.mask,
                                (
                                    land.rect.x - player.rect.x,
                                    land.rect.y - player.rect.y - 2,
                                ),
                            )
                            for land in objects
                        ):
                            jump_velocity = -GRAVITY * 2.5  # значение прыжка
                            jump_count += 1  # увеличиваем счётчик прыжков
                    if event.key == pygame.K_RETURN:
                        for (
                            interactive_object
                        ) in player_objects:  # на enter взаимодействие
                            if (
                                (
                                    player.rect.x + player.rect.width // 2 + 70
                                    > interactive_object.rect.x
                                )
                                and (
                                    player.rect.x + player.rect.width // 2 - 70
                                    < interactive_object.rect.x
                                    + interactive_object.rect.width
                                )
                                and (
                                    player.rect.y + player.rect.height // 2
                                    > interactive_object.rect.y
                                )
                                and (
                                    player.rect.y + player.rect.height // 2
                                    < interactive_object.rect.y
                                    + interactive_object.rect.height
                                )
                            ):
                                interactive_object.activate_touch_animation()  # взаимодействие с рычагом
                                interactive_object.switch_exit_conditions(
                                    exit_
                                )  # анимация рычага
                                if not all(
                                    exit_.exit_conditions
                                ):  # если нажатие не решило загадку, с шансом 1/12 олег скажет что-то грустное
                                    if randrange(12) == 4:
                                        oleg.stop()
                                        oleg = pygame.mixer.Sound(
                                            f"../assets/sounds/oleg_speak/{choice(os.listdir('../assets/sounds/oleg_speak'))}"
                                        )
                                        oleg.play()
                                break

                if (
                    event.type == pygame.USEREVENT
                ):  # если игрок согласился выйти, закрываем программу
                    if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                        pygame.quit()
                        sys.exit()
                manager.process_events(event)
            if keys_pressed[
                pygame.K_a
            ]:  # обработка wasd, понимаем куда игрок хочет двигаться
                move_left = -7
            else:
                move_left = 0
            if keys_pressed[pygame.K_d]:
                move_right = 7
            else:
                move_right = 0

            update_collision()  # функция коллизии

            object_update()  # передвижение объектов
            if jump_velocity < 0:  # уменьшаем прыжок со временем
                jump_velocity += 1
            manager.update(time_delta)  # обновление экрана
            all_sprites.draw(main_window)
            manager.draw_ui(main_window)
            indicator.draw_condition_circles()
            draw_jump_counter(main_window, jump_count)

            pygame.display.update()
            clock.tick(60)
        pygame.mixer.music.stop()  # останавливаем музыку
        main_window.blit(load_screen, (0, 0))  # очищаем экран и списки объектов
        pygame.display.update()
        for sprite in all_sprites:
            all_sprites.remove(sprite)
        objects.clear()
        player_objects.clear()

    end_screen()  # экран конца игры
