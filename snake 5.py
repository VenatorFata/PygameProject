import sys
import os
import pygame
import random
import math

# Инициализация Pygame и других модулей
pygame.init()
pygame.display.set_caption("Ярославская Змейка")  # Устанавливаем заголовок окна
pygame.font.init()  # Инициализация модуля шрифтов
random.seed()  # Инициализация генератора случайных чисел

# Список изображений фруктов
FRUIT_IMAGES = ["donat.png", "watermelon.png", "broccoly.png", "green.png", "strawberry.png"]

# Константы игры
SNAKE_SPEED = 2  # Скорость змейки
BLOCK_SIZE = 45  # Размер блока (змейка и фрукты)
FRUIT_SIZE = BLOCK_SIZE  # Размер фрукта
GAP = 10  # Расстояние между сегментами змейки
SCREEN_DIMENSION = 600  # Размер игрового окна
FPS_LIMIT = 15  # Ограничение FPS (кадров в секунду)

# Сопоставление клавиш с направлениями
KEY_MAPPING = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4}

# Инициализация списка фруктов и игрового окна
fruits = []
display = pygame.display.set_mode([SCREEN_DIMENSION, SCREEN_DIMENSION])  # Создание окна

# Шрифты для отображения счета и сообщений
font_score = pygame.font.Font(None, 38)
font_score_num = pygame.font.Font(None, 28)
font_game_over = pygame.font.Font(None, 46)
font_play_again = font_score_num

# Текст счета
score_text = font_score.render('Score: ', True, pygame.Color('green'))
score_text_size = font_score.size('Score')

# Цвета
bg_color = pygame.Color(15, 10, 15)  # Цвет фона
black_color = pygame.Color(0, 0, 0)  # Черный цвет

# Часы для контроля FPS
clock = pygame.time.Clock()


def check_collision(pos_a, size_a, pos_b, size_b):
    """
    Проверка столкновения между двумя объектами.
    Возвращает True, если объекты пересекаются.
    """
    return (pos_a.x < pos_b.x + size_b and pos_a.x + size_a > pos_b.x and
            pos_a.y < pos_b.y + size_b and pos_a.y + size_a > pos_b.y)


def exit_game():
    """Завершение игры и выход из программы."""
    pygame.quit()
    sys.exit()


def show_game_over():
    """Отображение экрана 'Game Over'."""
    over_message = font_game_over.render("Game Over", True, pygame.Color("white"))
    replay_message = font_play_again.render("Try again? Yes/No", True, pygame.Color("green"))
    display.blit(over_message, (320, 240))  # Отображение сообщения
    display.blit(replay_message, (320 + 12, 240 + 40))
    pygame.display.flip()  # Обновление экрана
    wait_for_input()  # Ожидание ввода пользователя


def wait_for_input():
    """Ожидание ввода пользователя после завершения игры."""
    while True:
        key = get_input()
        if key == "exit":
            exit_game()
        elif key == "yes":
            main()  # Перезапуск игры
        elif key == "no":
            exit_game()  # Выход из игры


def check_boundaries(snake):
    """Проверка границ экрана и телепортация змейки на противоположную сторону."""
    if snake.x > SCREEN_DIMENSION:
        snake.x = BLOCK_SIZE
    elif snake.x < 0:
        snake.x = SCREEN_DIMENSION - BLOCK_SIZE
    elif snake.y > SCREEN_DIMENSION:
        snake.y = BLOCK_SIZE
    elif snake.y < 0:
        snake.y = SCREEN_DIMENSION - BLOCK_SIZE


def load_image(name, colorkey=None, size=None):
    """
    Загрузка изображения из файла.
    Если указан colorkey, изображение будет прозрачным.
    Если указан size, изображение будет масштабировано.
    """
    fullname = os.path.join('data', name)  # Путь к файлу
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    # Масштабирование изображения, если указан размер
    if size is not None:
        image = pygame.transform.scale(image, size)

    return image


class SnakeBodySprite(pygame.sprite.Sprite):
    """Класс для спрайта тела змейки."""
    def __init__(self, x, y, size=(BLOCK_SIZE, BLOCK_SIZE)):
        super().__init__()
        self.image = load_image("snakebody2.png", size=(BLOCK_SIZE, BLOCK_SIZE))  # Загрузка изображения
        self.current_direction = 1  # Текущее направление
        self.rect = self.image.get_rect()  # Прямоугольник для позиционирования
        self.rect.topleft = (x, y)  # Установка позиции

    def update(self, x, y, direction):
        """Обновление спрайта тела змейки."""
        if self.current_direction != direction:
            # Поворот изображения в зависимости от направления
            if self.current_direction == KEY_MAPPING['UP']:
                if direction == KEY_MAPPING['LEFT']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['RIGHT']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['RIGHT']:
                if direction == KEY_MAPPING['UP']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['DOWN']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['DOWN']:
                if direction == KEY_MAPPING['RIGHT']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['LEFT']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['LEFT']:
                if direction == KEY_MAPPING['DOWN']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['UP']:
                    self.image = pygame.transform.rotate(self.image, -90)
            self.current_direction = direction
        self.rect.topleft = (x, y)  # Обновление позиции


class SnakeHeadSprite(pygame.sprite.Sprite):
    """Класс для спрайта головы змейки."""
    def __init__(self, x, y, size=(BLOCK_SIZE, BLOCK_SIZE)):
        super().__init__()
        self.image = load_image("snakehead2.png", size=(BLOCK_SIZE, BLOCK_SIZE))  # Загрузка изображения
        self.current_direction = 1  # Текущее направление
        self.rect = self.image.get_rect()  # Прямоугольник для позиционирования
        self.rect.topleft = (x, y)  # Установка позиции

    def update(self, x, y, direction):
        """Обновление спрайта головы змейки."""
        if self.current_direction != direction:
            # Поворот изображения в зависимости от направления
            if self.current_direction == KEY_MAPPING['UP']:
                if direction == KEY_MAPPING['LEFT']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['RIGHT']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['RIGHT']:
                if direction == KEY_MAPPING['UP']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['DOWN']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['DOWN']:
                if direction == KEY_MAPPING['RIGHT']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['LEFT']:
                    self.image = pygame.transform.rotate(self.image, -90)
            elif self.current_direction == KEY_MAPPING['LEFT']:
                if direction == KEY_MAPPING['DOWN']:
                    self.image = pygame.transform.rotate(self.image, 90)
                elif direction == KEY_MAPPING['UP']:
                    self.image = pygame.transform.rotate(self.image, -90)
            self.current_direction = direction
        self.rect.topleft = (x, y)  # Обновление позиции


class FruitSprite(pygame.sprite.Sprite):
    """Класс для спрайта фрукта."""
    def __init__(self, x, y, image_name, size=(FRUIT_SIZE, FRUIT_SIZE)):
        super().__init__()
        self.image = load_image(image_name, size=size)  # Загрузка изображения фрукта
        self.rect = self.image.get_rect()  # Прямоугольник для позиционирования
        self.rect.topleft = (x, y)  # Установка позиции

    def update(self, x, y):
        """Обновление позиции фрукта."""
        self.rect.topleft = (x, y)


class Fruit:
    """Класс для фрукта."""
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state
        # Выбор случайного изображения фрукта
        random_fruit_image = random.choice(FRUIT_IMAGES)
        self.sprite = FruitSprite(self.x, self.y, random_fruit_image, size=(FRUIT_SIZE, FRUIT_SIZE))

    def draw(self, surface):
        """Отрисовка фрукта на экране."""
        if self.state == 1:
            self.sprite.update(self.x, self.y)
            surface.blit(self.sprite.image, self.sprite.rect)


class SnakeSegment:
    """Класс для сегмента змейки."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY_MAPPING['UP']  # Направление сегмента
        self.color = 'white'  # Цвет сегмента


class Snake:
    """Класс для змейки."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY_MAPPING['UP']  # Направление змейки
        self.body = []  # Список сегментов тела
        self.body.append(self)  # Добавление головы в тело

        # Спрайты для змейки
        self.sprite_group = pygame.sprite.Group()  # Группа для спрайтов тела
        self.head_sprite = SnakeHeadSprite(self.x, self.y, size=(BLOCK_SIZE, BLOCK_SIZE))  # Спрайт головы

        # Добавление начальных сегментов тела
        for i in range(1, 4):  # Начальная длина змейки (3 сегмента)
            tail_segment = SnakeSegment(self.x, self.y + i * GAP)
            tail_segment.direction = KEY_MAPPING['UP']
            tail_segment.color = 'NULL'
            self.body.append(tail_segment)
            body_sprite = SnakeBodySprite(tail_segment.x, tail_segment.y, size=(BLOCK_SIZE, BLOCK_SIZE))
            self.sprite_group.add(body_sprite)

    def move(self):
        """Движение змейки."""
        last_index = len(self.body) - 1
        while last_index != 0:
            # Обновление направления и позиции сегментов
            self.body[last_index].direction = self.body[last_index - 1].direction
            self.body[last_index].x = self.body[last_index - 1].x
            self.body[last_index].y = self.body[last_index - 1].y
            last_index -= 1

        if len(self.body) < 2:
            last_segment = self
        else:
            last_segment = self.body.pop(last_index)

        last_segment.direction = self.body[0].direction
        if self.body[0].direction == KEY_MAPPING["UP"]:
            last_segment.y = self.body[0].y - (SNAKE_SPEED * FPS_LIMIT)
        elif self.body[0].direction == KEY_MAPPING["DOWN"]:
            last_segment.y = self.body[0].y + (SNAKE_SPEED * FPS_LIMIT)
        elif self.body[0].direction == KEY_MAPPING["LEFT"]:
            last_segment.x = self.body[0].x - (SNAKE_SPEED * FPS_LIMIT)
        elif self.body[0].direction == KEY_MAPPING["RIGHT"]:
            last_segment.x = self.body[0].x + (SNAKE_SPEED * FPS_LIMIT)

        self.body.insert(0, last_segment)

        # Обновление спрайтов
        for i, segment in enumerate(self.body):
            if i == 0:
                # Обновление спрайта головы
                self.head_sprite.update(segment.x, segment.y, self.direction)
            else:
                # Обновление спрайтов тела
                body_sprite = list(self.sprite_group)[i - 1]  # Индексы сдвинуты на 1
                body_sprite.update(segment.x, segment.y, segment.direction)

    def grow(self):
        """Увеличение длины змейки."""
        last_index = len(self.body) - 1
        new_segment = SnakeSegment(self.body[last_index].x, self.body[last_index].y)

        if self.body[last_index].direction == KEY_MAPPING["UP"]:
            new_segment.y += BLOCK_SIZE
        elif self.body[last_index].direction == KEY_MAPPING["DOWN"]:
            new_segment.y -= BLOCK_SIZE
        elif self.body[last_index].direction == KEY_MAPPING["LEFT"]:
            new_segment.x += BLOCK_SIZE
        elif self.body[last_index].direction == KEY_MAPPING["RIGHT"]:
            new_segment.x -= BLOCK_SIZE

        self.body.append(new_segment)

        # Добавление спрайта для нового сегмента
        body_sprite = SnakeBodySprite(new_segment.x, new_segment.y, size=(BLOCK_SIZE, BLOCK_SIZE))
        self.sprite_group.add(body_sprite)

    def set_direction(self, direction):
        """Установка направления змейки."""
        if (self.direction == KEY_MAPPING["RIGHT"] and direction == KEY_MAPPING["LEFT"]) or \
           (self.direction == KEY_MAPPING["LEFT"] and direction == KEY_MAPPING["RIGHT"]):
            pass
        elif (self.direction == KEY_MAPPING["UP"] and direction == KEY_MAPPING["DOWN"]) or \
             (self.direction == KEY_MAPPING["DOWN"] and direction == KEY_MAPPING["UP"]):
            pass
        else:
            self.direction = direction

    def get_head(self):
        """Получение головы змейки."""
        return self.body[0]

    def is_collided(self):
        """Проверка столкновения змейки с самой собой."""
        for i in range(1, len(self.body) - 1):
            if check_collision(self.body[0], BLOCK_SIZE, self.body[i], BLOCK_SIZE) and self.body[i].color != "NULL":
                return True
        return False

    def draw(self, surface):
        """Отрисовка змейки на экране."""
        # Сначала отрисовываем тело
        self.sprite_group.draw(surface)
        # Затем отрисовываем голову поверх тела
        surface.blit(self.head_sprite.image, self.head_sprite.rect)


def get_input():
    """Получение ввода от пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return KEY_MAPPING["UP"]
            elif event.key == pygame.K_DOWN:
                return KEY_MAPPING["DOWN"]
            elif event.key == pygame.K_LEFT:
                return KEY_MAPPING["LEFT"]
            elif event.key == pygame.K_RIGHT:
                return KEY_MAPPING["RIGHT"]
            elif event.key == pygame.K_ESCAPE:
                return "exit"
            elif event.key == pygame.K_y:
                return "yes"
            elif event.key == pygame.K_n:
                exit_game()
        if event.type == pygame.QUIT:
            exit_game()


def respawn_fruits(snake_x, snake_y):
    radius = math.sqrt((SCREEN_DIMENSION / 2) ** 2 + (SCREEN_DIMENSION / 2) ** 2) / 2
    fruits.clear()
    angle = 999
    while angle > radius:
        angle = random.uniform(0, 800) * math.pi * 2
        x = int(SCREEN_DIMENSION / 2 + radius * math.cos(angle))
        y = int(SCREEN_DIMENSION / 2 + radius * math.sin(angle))
        if x == snake_x and y == snake_y:
            continue
    new_fruit = Fruit(x - x % BLOCK_SIZE, y - y % BLOCK_SIZE, 1)
    fruits.append(new_fruit)


def display_score(current_score):
    score_number = font_score_num.render(str(current_score), True, pygame.Color('red'))
    display.blit(score_text, (SCREEN_DIMENSION - score_text_size[0] - 60, 10))
    display.blit(score_number, (SCREEN_DIMENSION - 45, 14))


def display_game_time(game_time):
    time_text = font_score.render('Time: ', True, pygame.Color('red'))
    time_number = font_score_num.render(str(game_time / 1000), True, pygame.Color("red"))
    display.blit(time_text, (30, 10))
    display.blit(time_number, (105, 14))


def main():
    score = 0
    player_snake = Snake(SCREEN_DIMENSION / 2 - SCREEN_DIMENSION / 2 % BLOCK_SIZE,
                         SCREEN_DIMENSION / 2 - SCREEN_DIMENSION / 2 % BLOCK_SIZE)
    player_snake.set_direction(KEY_MAPPING["UP"])

    # Добавляем начальные сегменты тела
    for _ in range(3):
        player_snake.grow()
        player_snake.move()

    for _ in range(3):
        player_snake.grow()
        player_snake.move()

    apple_count = 1
    fruit_eaten = False
    fruit_x, fruit_y = random.randint(60, SCREEN_DIMENSION), random.randint(60, SCREEN_DIMENSION)
    fruit_x, fruit_y = fruit_x - fruit_x % BLOCK_SIZE, fruit_y - fruit_y % BLOCK_SIZE
    initial_fruit = Fruit(fruit_x, fruit_y, 1)
    fruits.append(initial_fruit)
    respawn_fruits(player_snake.x, player_snake.y)

    start_time = pygame.time.get_ticks()
    game_running = True

    while game_running:
        clock.tick(FPS_LIMIT)
        key_press = get_input()
        if key_press == 'exit':
            game_running = False

        check_boundaries(player_snake)

        if player_snake.is_collided():
            show_game_over()

        if key_press:
            player_snake.set_direction(key_press)

        player_snake.move()

        for fruit in fruits:
            if fruit.state == 1 and check_collision(player_snake.get_head(), BLOCK_SIZE, fruit, FRUIT_SIZE):
                player_snake.grow()
                fruit.state = 0
                score += 1
                fruit_eaten = True

        if fruit_eaten:
            fruit_eaten = False
            respawn_fruits(player_snake.get_head().x, player_snake.get_head().y)

        display.fill(bg_color)

        for fruit in fruits:
            if fruit.state == 1:
                fruit.draw(display)

        player_snake.draw(display)
        display_score(score)

        current_time = pygame.time.get_ticks() - start_time
        display_game_time(current_time)
        #print(player_snake.x, player_snake.y, fruit.x, fruit.y)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()