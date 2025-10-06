import pygame
import random
import sys
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Определяем размер экрана динамически
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption(":)")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
COLORS = [
    (255, 0, 0),    # Красный
    (0, 255, 0),    # Зелёный
    (255, 255, 0),  # Жёлтый
    (0, 0, 255),    # Синий
    (255, 0, 255),  # Пурпурный
    (0, 255, 255),  # Голубой
    (255, 255, 255) # Белый
]

# Ретро-ёлка
TREE = [
    "       *        ",
    "      ***       ",
    "     *****      ",
    "    *******     ",
    "   *********    ",
    "  ***********   ",
    " *************  ",
    "*************** ",
    "      |||       ",
    "      |||       "
]

# Масштабирование
scale_factor = min(WIDTH / 1920, HEIGHT / 1080)

# Снежинки (плотнее)
snowflakes = []
snowflakes_count = int(300 * scale_factor)  # Увеличено количество
for _ in range(snowflakes_count):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.uniform(0.5, 1.5)
    size = int(2 * scale_factor + 2)
    snowflakes.append([x, y, speed, size])

# Тайминги субтитров
lyrics = [
    (45,  "Last Christmas, I gave you my heart"),
    (49,  "But the very next day, you gave it away"),
    (53,  "This year, to save me from tears"),
    (57,  "I'll give it to someone special"),
    (61,  ""),
    (62,  "Last Christmas, I gave you my heart"),
    (67,  "But the very next day, you gave it away"),
    (70,  "This year, to save me from tears"),
    (74,  "I'll give it to someone special"),
]

# Путь к аудиофайлу
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

music_file = resource_path("last_christmas.mp3")

# Шрифты (масштабируемые)
font_tree = pygame.font.SysFont("Courier", int(30 * scale_factor))
font_lyrics = pygame.font.SysFont("Arial", int(20 * scale_factor), bold=True)
font_secret = pygame.font.SysFont("Impact", int(400 * scale_factor), bold=False)

# Переменные для пасхалки
taps = 0
last_tap_time = 0
secret_active = False
secret_timer = 0

# Загрузка музыки
try:
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(start=45.0)
except Exception as e:
    print(f"Ошибка загрузки музыки: {e}")
    sys.exit(1)

def draw_tree(lights):
    tree_center_x = WIDTH // 2
    tree_center_y = HEIGHT // 2
    for i, row in enumerate(TREE):
        for j, char in enumerate(row):
            if char == "*":
                if lights[i][j]:
                    color = random.choice(COLORS)
                    text = font_tree.render(char, True, color)
                else:
                    text = font_tree.render(char, True, WHITE)
                x_pos = tree_center_x - int(60 * scale_factor) + j * int(8 * scale_factor)
                y_pos = tree_center_y - int(80 * scale_factor) + i * int(18 * scale_factor)
                screen.blit(text, (x_pos, y_pos))
            elif char == "|":
                text = font_tree.render(char, True, BROWN)
                screen.blit(text, (x_pos, y_pos))

def update_snowflakes():
    for flake in snowflakes:
        flake[1] += flake[2]
        if flake[1] > HEIGHT:
            flake[1] = 0
            flake[0] = random.randint(0, WIDTH)

def draw_snowflakes():
    for flake in snowflakes:
        pygame.draw.circle(screen, WHITE, (int(flake[0]), int(flake[1])), flake[3])

def draw_lyrics(current_time):
    current_lyric = ""
    for time, text in lyrics:
        if current_time >= time and current_time < time + 4:
            current_lyric = text
    if current_lyric:
        text = font_lyrics.render(current_lyric, True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - int(70 * scale_factor)))

def draw_secret():
    if secret_active:
        if int(pygame.time.get_ticks() / 300) % 2 == 0:
            text = font_secret.render("СОСАЛ?", True, RED)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

def main():
    global taps, last_tap_time, secret_active, secret_timer
    lights = [[random.choice([True, False]) for _ in range(15)] for _ in range(8)]
    clock = pygame.time.Clock()
    running = True
    current_time = 45

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.FINGERDOWN:  # Тапы для Android
                current_time_ms = pygame.time.get_ticks()
                if current_time_ms - last_tap_time < 10000:  # 10 секунд на 5 тапов
                    taps += 1
                    if taps >= 5:
                        secret_active = True
                        secret_timer = pygame.time.get_ticks()
                else:
                    taps = 1
                last_tap_time = current_time_ms

        screen.fill(BLACK)
        draw_tree(lights)
        update_snowflakes()
        draw_snowflakes()
        draw_lyrics(current_time)
        draw_secret()

        # Обновляем гирлянду
        for i in range(8):
            for j in range(15):
                if TREE[i][j] == "*" and random.random() < 0.3:
                    lights[i][j] = random.choice([True, False])

        if pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000 + 45
        else:
            current_time += 1 / 30

        # Закрытие после второго куплета (~90с)
        if current_time >= 90:
            running = False

        # Сброс пасхалки через 3 секунды
        if secret_active and pygame.time.get_ticks() - secret_timer > 3000:
            secret_active = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
