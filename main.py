import pygame
import os
import sys
from random import choice
import time
from db import Db
pygame.init()
db = Db()
scores = int()
time_ = None
running = True
level = None
distance = None
delay = None


def write_result():
    global scores, level
    db.add_result(level, scores)
    db.close()


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
    write_result()
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
    write_result()
    intro_text = [f"U've passed the {level} level!",
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
    images = ["cloud.png", "cloudO.png"]
    POSITIONS_X = [10, 200]

    def __init__(self, *group):
        super().__init__(*group)
        self.name = choice(Cloud.images)
        self.image = load_image(self.name)
        self.rect = self.image.get_rect()
        self.rect.x = choice(Cloud.POSITIONS_X)
        self.rect.y = 700
        self.speedy = 1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global scores
        if not pygame.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        else:
            if self.name == "cloud.png":
                end_screen()
            else:
                scores += 1
                self.kill()


horizontal_borders = pygame.sprite.Group()
borders = pygame.sprite.Group()


class BorderForSkydiver(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        self.add(horizontal_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (204, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def main():
    global running, distance, level, delay, time_, scores

    start_screen()

    if level == 1:
        distance = 190
        delay = 0.015
    elif level == 2:
        distance = 170
        delay = 0.01
    elif level == 3:
        distance = 150
        delay = 0.005
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
            break
        seconds = (pygame.time.get_ticks() - start_ticks) / \
            1000
        if seconds > 300:
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

        draw_text(screen, str(scores), 18, WIDTH / 2, 10)

        skydivers.draw(screen)
        clouds.draw(screen)
        skydivers.update()
        clouds.update()

        pygame.display.flip()
    pygame.quit()
    clock.tick(FPS)


if __name__ == "__main__":
    main()
# add some animation to collide
# add cloud counting
# add some birds
# add registration (down the screen)
