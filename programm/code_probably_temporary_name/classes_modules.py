import sys
import os
import pygame
import pygame_gui

# константы экрана
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode(SCREEN_SIZE)
screen.fill("white")


def load_image(filename, colorkey=None):  # функция загрузки картинки
    full_path = os.path.join("../assets", filename)
    if not os.path.isfile(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        sys.exit()

    loaded_image = pygame.image.load(full_path)
    if colorkey is not None:
        loaded_image = loaded_image.convert()
        if colorkey == -1:
            colorkey = loaded_image.get_at((0, 0))
        loaded_image.set_colorkey(colorkey)
    else:
        loaded_image = loaded_image.convert_alpha()
    return loaded_image


class Land(pygame.sprite.Sprite):  # платформа
    def __init__(self, image_name, pos_x, pos_y, platform_width, platform_height):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(pos_x, pos_y, platform_width, platform_height)
        self.image = pygame.transform.smoothscale(
            load_image(f"fons/{image_name}"), self.rect.size
        )
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):  # игрок
    def __init__(self, image_name, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.idle_image = pygame.transform.smoothscale(
            load_image(f"objects/{image_name}"), (64, 64)
        )
        self.image = self.idle_image
        self.orientation = 1
        self.current_frame = 0
        self.run_animation_frames = []
        self.fall_animation_frames = []
        self.animation_status = "idle"

        # анимации
        self.cut_animation_sheet(
            load_image(f"objects/tinkoff_run.png"), 20, 1, self.run_animation_frames
        )
        self.cut_animation_sheet(
            load_image(f"objects/tinkoff_fall_from_stratosphere.png"),
            10,
            1,
            self.fall_animation_frames,
        )

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def cut_animation_sheet(
        self, sprite_sheet, columns, rows, frame_list
    ):  # режем анимацию на кадры
        frame_rect = pygame.Rect(
            0, 0, sprite_sheet.get_width() // columns, sprite_sheet.get_height() // rows
        )
        for row in range(rows):
            for column in range(columns):
                frame_position = (frame_rect.w * column, frame_rect.h * row)
                frame_list.append(
                    sprite_sheet.subsurface(
                        pygame.Rect(frame_position, frame_rect.size)
                    )
                )

    def update_run_animation(self):  # проигрывание бега
        if self.animation_status != "run":
            self.animation_status = "run"
            self.current_frame = 0

        self.image = self.run_animation_frames[self.current_frame]
        if self.orientation < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.current_frame = (self.current_frame + 1) % len(self.run_animation_frames)

    def update_fall_animation(self):  # анимация падения
        if self.animation_status != "fall":
            self.animation_status = "fall"
            self.current_frame = 0

        self.image = self.fall_animation_frames[self.current_frame]
        if self.orientation < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.current_frame = (self.current_frame + 1) % len(self.fall_animation_frames)

    def update_idle_animation(self):  # анимация спокойствия
        self.image = self.idle_image
        if self.orientation < 0:
            self.image = pygame.transform.flip(self.image, True, False)


class Wall(pygame.sprite.Sprite):  # стенки
    def __init__(self, image_name, pos_x, pos_y, wall_width, wall_height):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(pos_x, pos_y, wall_width, wall_height)
        self.image = pygame.transform.smoothscale(
            load_image(f"fons/{image_name}"), self.rect.size
        )
        self.mask = pygame.mask.from_surface(self.image)


class Lever(pygame.sprite.Sprite):  # рычаг
    def __init__(
        self, image_name, pos_x, pos_y, lever_width, lever_height, *switch_conditions
    ):
        super().__init__(all_sprites)
        self.lever_sound = pygame.mixer.Sound("../assets/sounds/lever_sound.mp3")
        self.lever_sound.set_volume(0.3)
        # меняет определённые значения в выходе, чтобы вышли своего рода пятнашки
        self.switch_conditions = switch_conditions
        self.rect = pygame.Rect(pos_x, pos_y, lever_width, lever_height)
        self.image = pygame.transform.smoothscale(
            load_image(f"objects/{image_name}"), self.rect.size
        )
        self.mask = pygame.mask.from_surface(self.image)

    def activate_touch_animation(self):  # анимация переключения
        self.lever_sound.play()
        self.image = pygame.transform.flip(self.image, True, False)

    def switch_exit_conditions(self, exit_object):  # переключение
        for condition_index in self.switch_conditions:
            exit_object.exit_conditions[condition_index - 1] = (
                not exit_object.exit_conditions[condition_index - 1]
            )


class Exit(pygame.sprite.Sprite):  # выход
    def __init__(
        self, image_name, pos_x, pos_y, exit_width, exit_height, condition_count
    ):
        super().__init__(all_sprites)
        # хранит информацию, сколько условий нужно для выхода
        self.exit_conditions = [False for i in range(condition_count)]
        self.is_exit_available = False
        self.rect = pygame.Rect(pos_x, pos_y, exit_width, exit_height)
        self.image = pygame.transform.smoothscale(
            load_image(f"objects/{image_name}"), self.rect.size
        )
        self.mask = pygame.mask.from_surface(self.image)

    def check_all_conditions_completed(self):  # если всё выполнено, то можно выйти
        if all(self.exit_conditions):
            self.is_exit_available = True


class Portal(pygame.sprite.Sprite):  # портал
    def __init__(
        self, image_name, portal_direction, portal_id, target_portal_id, pos_x, pos_y
    ):
        super().__init__(all_sprites)
        self.portal_id = portal_id  # есть свой id
        self.target_portal_id = target_portal_id  # и id другого портала
        self.portal_sound = pygame.mixer.Sound("../assets/sounds/portal.mp3")
        self.portal_sound.set_volume(0.05)
        self.portal_direction = portal_direction  # направление, куда смотрит
        self.rect = pygame.Rect(pos_x, pos_y, 64, 128)
        self.image = pygame.transform.smoothscale(
            load_image(f"objects/{image_name}"), self.rect.size
        )
        # картинку переворачиваем если надо
        if self.portal_direction == "right":
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)


class Indicator:  # кружочки слева сверху
    def __init__(self, game_surface, exit_object):
        self.indicator_conditions = exit_object.exit_conditions
        self.game_screen = game_surface
        self.indicator_colors = {True: "green", False: "red"}

    def draw_condition_circles(self):
        circle_x_offset = 42
        for condition_index in range(len(self.indicator_conditions)):
            pygame.draw.circle(
                self.game_screen,
                pygame.Color(
                    self.indicator_colors[self.indicator_conditions[condition_index]]
                ),
                (circle_x_offset * (condition_index + 1), 30),
                20,
            )


# спрайты
horizontal_borders = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_image = pygame.transform.scale(load_image("objects/lico.jpg"), (64, 64))
