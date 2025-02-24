import sys
import os
import pygame
import random
import math

pygame.init()
pygame.display.set_caption("Ярославская Змейка")
pygame.font.init()
random.seed()

SNAKE_SPEED = 2
BLOCK_SIZE = 20
FRUIT_SIZE = BLOCK_SIZE
GAP = 10
SCREEN_DIMENSION = 600
FPS_LIMIT = 10

KEY_MAPPING = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4}
fruits = []
display = pygame.display.set_mode([SCREEN_DIMENSION, SCREEN_DIMENSION])
font_score = pygame.font.Font(None, 38)
font_score_num = pygame.font.Font(None, 28)
font_game_over = pygame.font.Font(None, 46)
font_play_again = font_score_num

score_text = font_score.render('Score: ', True, pygame.Color('green'))
score_text_size = font_score.size('Score')
bg_color = pygame.Color(15, 10, 15)
black_color = pygame.Color(0, 0, 0)
clock = pygame.time.Clock()


def check_collision(pos_a, size_a, pos_b, size_b):
    return (pos_a.x < pos_b.x + size_b and pos_a.x + size_a > pos_b.x and
            pos_a.y < pos_b.y + size_b and pos_a.y + size_a > pos_b.y)


def exit_game():
    pygame.quit()
    sys.exit()


def show_game_over():
    over_message = font_game_over.render("Game Over", True, pygame.Color("white"))
    replay_message = font_play_again.render("Try again? Yes/No", True, pygame.Color("green"))
    display.blit(over_message, (320, 240))
    display.blit(replay_message, (320 + 12, 240 + 40))
    pygame.display.flip()
    wait_for_input()


def wait_for_input():
    while True:
        key = get_input()
        if key == "exit":
            exit_game()
        elif key == "yes":
            main()
        elif key == "no":
            exit_game()


def check_boundaries(snake):
    if snake.x > SCREEN_DIMENSION:
        snake.x = BLOCK_SIZE
    elif snake.x < 0:
        snake.x = SCREEN_DIMENSION - BLOCK_SIZE
    elif snake.y > SCREEN_DIMENSION:
        snake.y = BLOCK_SIZE
    elif snake.y < 0:
        snake.y = SCREEN_DIMENSION - BLOCK_SIZE


class Fruit:
    def __init__(self, x, y, state):
        self.x = int(x)
        self.y = int(y)
        self.state = state
        self.color = pygame.Color('red')

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, FRUIT_SIZE, FRUIT_SIZE))


class SnakeSegment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY_MAPPING['UP']
        self.color = 'white'


class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = KEY_MAPPING['UP']
        self.body = []
        self.body.append(self)

        tail_segment = SnakeSegment(self.x, self.y + GAP)
        tail_segment.direction = KEY_MAPPING['UP']
        tail_segment.color = 'NULL'
        self.body.append(tail_segment)

    def move(self):
        last_index = len(self.body) - 1
        while last_index != 0:
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

    def grow(self):
        last_index = len(self.body) - 1
        self.body[last_index].direction = self.body[last_index].direction
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

    def set_direction(self, direction):
        if (self.direction == KEY_MAPPING["RIGHT"] and direction == KEY_MAPPING["LEFT"]) or \
           (self.direction == KEY_MAPPING["LEFT"] and direction == KEY_MAPPING["RIGHT"]):
            pass
        elif (self.direction == KEY_MAPPING["UP"] and direction == KEY_MAPPING["DOWN"]) or \
             (self.direction == KEY_MAPPING["DOWN"] and direction == KEY_MAPPING["UP"]):
            pass
        else:
            self.direction = direction

    def get_head(self):
        return self.body[0]

    def is_collided(self):
        for i in range(1, len(self.body) - 1):
            if check_collision(self.body[0], BLOCK_SIZE, self.body[i], BLOCK_SIZE) and self.body[i].color != "NULL":
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color('yellow'), (self.body[0].x, self.body[0].y, BLOCK_SIZE, BLOCK_SIZE), 0)
        for segment in self.body[1:]:
            if segment.color != 'NULL':
                pygame.draw.rect(surface, pygame.Color('white'), (segment.x, segment.y, BLOCK_SIZE, BLOCK_SIZE), 0)

def get_input():
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
        print(player_snake.x, player_snake.y, fruit.x, fruit.y)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()


