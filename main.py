import pygame
import os
import sys
from random import choice
import time
pygame.init()

running = True


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


def start_screen():
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
                    return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except FileNotFoundError as message:
        print(f'File {filename} not found')
        raise SystemExit(message)


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
        global running
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            running = False


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
        global running
        if not pygame.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        else:
            running = False


horizontal_borders = pygame.sprite.Group()
borders = pygame.sprite.Group()


class BorderForSkydiver(pygame.sprite.Sprite):

    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)

        self.add(horizontal_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def main():
    global running
    start_screen()
    clouds = pygame.sprite.Group()
    pygame.mouse.set_visible(False)
    counter = 189
    BorderForSkydiver(5, 5, WIDTH - 5, 5)
    '''
    BorderForSkydiver(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    BorderForSkydiver(5, 5, 5, HEIGHT - 5)
    BorderForSkydiver(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
    '''

    while running:
        counter += 1
        if counter == 190:
            counter = 0
            Cloud(clouds)
        time.sleep(0.01)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
