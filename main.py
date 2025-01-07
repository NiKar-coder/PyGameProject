import pygame
import os
import sys
from random import choice
import time
from db import Db
pygame.init()
db = Db()

time_ = None
running = True
level = None
distance = None
delay = None


def load_image(name, colorkey=None):
    fullname = os.path.join("data/images/", name)
    try:
        image = pygame.image.load(fullname)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except pygame.error as message:
        print(f'Image {name} not found!')
        raise SystemExit(message)


def load_music(name):
    fullname = os.path.join("data/music/", name)
    try:
        melody = pygame.mixer.music.load(fullname)
        pygame.mixer.music.play(-1)
        return melody
    except pygame.error as message:
        print(f'Melody {name} not found!')
        raise SystemExit(message)


SIZE = WIDTH, HEIGHT = 300, 700
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
pygame.display.set_icon(load_image("skydiver.png"))
FPS = 60
load_music('melody.mp3')
pygame.display.set_caption("Skydiver")


def terminate():
    pygame.quit()
    sys.exit()


def end_screen():
    global running
    intro_text = ['Game over!',
                  'Press "ESC" to exit']
    screen.fill((115, 195, 225))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return
        pygame.display.flip()
        clock.tick(FPS)


def victory_screen():
    global running
    intro_text = [f"U've passed {level} level!",
                  'Press "ESC" to exit']
    db.add_result(level)
    screen.fill((115, 195, 225))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    global level, running
    intro_text = ['Press key from "1" to "3"',
                  'to choose level']
    screen.fill((115, 195, 225))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    level = 1
                    return  # начинаем игру
                if event.key == pygame.K_2:
                    level = 2
                    return  # начинаем игру
                if event.key == pygame.K_3:
                    level = 3
                    return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Skydiver(pygame.sprite.Sprite):
    image = load_image("skydiver.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Skydiver.image
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.speedy = 1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            end_screen()


skydivers = pygame.sprite.Group()
skydiver = Skydiver(skydivers)


class Cloud(pygame.sprite.Sprite):
    image = load_image("cloud.png")
    POSITIONS_X = [10, 200]

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Cloud.image
        self.rect = self.image.get_rect()
        self.rect.x = choice(Cloud.POSITIONS_X)
        self.rect.y = 700
        self.speedy = 1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if not pygame.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        else:
            end_screen()


horizontal_borders = pygame.sprite.Group()
borders = pygame.sprite.Group()


class BorderForSkydiver(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        self.add(horizontal_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def main():
    global running, distance, level, delay, time_

    start_screen()

    if level == 1:
        distance = 190
        delay = 0.015
        time_ = 60
    elif level == 2:
        distance = 170
        time_ = 20
        delay = 0.01
    elif level == 3:
        distance = 150
        delay = 0.005
        time_ = 10
    start_ticks = pygame.time.get_ticks()
    clouds = pygame.sprite.Group()
    pygame.mouse.set_visible(False)
    counter = distance - 1
    BorderForSkydiver(5, 5, WIDTH - 5, 5)
    BorderForSkydiver(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    BorderForSkydiver(5, 5, 5, HEIGHT - 5)
    BorderForSkydiver(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)

    while True:
        if not running:
            db.close()
            break
        seconds = (pygame.time.get_ticks() - start_ticks) / \
            1000
        if seconds > time_:
            victory_screen()
        counter += 1
        if counter == distance:
            counter = 0
            Cloud(clouds)
        time.sleep(delay)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                db.close()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    skydiver.rect.x = 200
                elif event.key == pygame.K_LEFT:
                    skydiver.rect.x = 10
                elif event.key == pygame.K_DOWN:
                    skydiver.rect.y += 30
                elif event.key == pygame.K_UP:
                    skydiver.rect.y -= 30
        screen.fill((115, 195, 225))
        skydivers.draw(screen)
        clouds.draw(screen)
        skydivers.update()
        clouds.update()

        pygame.display.flip()
    pygame.quit()
    clock.tick(FPS)


if __name__ == "__main__":
    main()
