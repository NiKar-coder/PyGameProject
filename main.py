import pygame as pg
import os
import sys
from random import choice
import time
from db import Db
pg.init()
db = Db()
scores = int()
time_ = None
running = True
level = None
distance = None
delay = None
COLOR_INACTIVE = pg.Color(136, 138, 133)
COLOR_ACTIVE = pg.Color(0, 0, 0)
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    return self.text
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


def write_result():
    global scores, level
    db.add_result(level, scores)
    db.close()


def load_image(name, colorkey=None):
    fullname = os.path.join("data/images/", name)
    try:
        image = pg.image.load(fullname)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except pg.error as message:
        print(f'Image {name} not found!')
        raise SystemExit(message)


def load_music(name):
    fullname = os.path.join("data/music/", name)
    try:
        melody = pg.mixer.music.load(fullname)
        pg.mixer.music.play(-1)
        return melody
    except pg.error as message:
        print(f'Melody {name} not found!')
        raise SystemExit(message)


SIZE = WIDTH, HEIGHT = 300, 700
screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
pg.display.set_icon(load_image("skydiver.png"))
FPS = 60
load_music('melody.mp3')
pg.display.set_caption("Skydiver")


def terminate():
    pg.quit()
    sys.exit()


def end_screen():
    global running
    write_result()
    intro_text = ['Game over!',
                  'Press "ESC" to exit']
    screen.fill((115, 195, 225))
    font = pg.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pg.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                    return
        pg.display.flip()
        clock.tick(FPS)


def victory_screen():
    global running
    write_result()
    intro_text = [f"U've passed the {level} level!",
                  'Press "ESC" to exit']

    font = pg.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pg.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                    return
        pg.display.flip()
        clock.tick(FPS)


def start_screen():
    global level, running

    input_box1 = InputBox(95, 30, 140, 32)
    input_box2 = InputBox(95, 100, 140, 32)
    input_box3 = InputBox(95, 170, 140, 32)
    input_boxes = [input_box1, input_box2, input_box3]
    arr = list()
    font_ = pg.font.SysFont('z003', 24)
    text2 = font_.render("Password", True,
                         (0, 0, 0))
    text1 = font_.render("Login", True,
                         (0, 0, 0))
    text3 = font_.render("Level", True,
                         (0, 0, 0))

    while True:
        if len(arr) == 3:
            if db.login(arr[0], arr[1]):
                level = int(arr[2])
                return
            else:
                arr = list()

        for event in pg.event.get():
            for box in input_boxes:
                el = box.handle_event(event)
                if el:
                    arr.append(el)
        for box in input_boxes:
            box.update()
        screen.fill((115, 195, 225))
        for box in input_boxes:
            box.draw(screen)
        screen.blit(text2, (5, 105))
        screen.blit(text1, (5, 35))
        screen.blit(text3, (5, 175))
        pg.display.flip()
        clock.tick(FPS)


class Skydiver(pg.sprite.Sprite):
    image = load_image("skydiver.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Skydiver.image
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.speedy = 1
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        if pg.sprite.spritecollideany(self, horizontal_borders):
            end_screen()


skydivers = pg.sprite.Group()
skydiver = Skydiver(skydivers)


class Cloud(pg.sprite.Sprite):
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
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        global scores
        if not pg.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        else:
            if self.name == "cloud.png":
                end_screen()
            else:
                scores += 1
                self.kill()


horizontal_borders = pg.sprite.Group()
borders = pg.sprite.Group()


class BorderForSkydiver(pg.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        self.add(horizontal_borders)
        self.image = pg.Surface([x2 - x1, 1])
        self.rect = pg.Rect(x1, y1, x2 - x1, 1)


font_name = pg.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, (204, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def main():
    global running, distance, level, delay, time_, scores
    start_screen()

    if level == 1:
        distance = 170
        delay = 0.01
    elif level == 2:
        distance = 170
        delay = 0.007
    elif level == 3:
        distance = 150
        delay = 0.002
    start_ticks = pg.time.get_ticks()
    clouds = pg.sprite.Group()
    # pg.mouse.set_visible(False)
    counter = distance - 1
    BorderForSkydiver(5, 5, WIDTH - 5, 5)
    BorderForSkydiver(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    BorderForSkydiver(5, 5, 5, HEIGHT - 5)
    BorderForSkydiver(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)

    while True:
        if not running:
            break
        seconds = (pg.time.get_ticks() - start_ticks) / \
            1000
        if seconds > 300:
            victory_screen()
        counter += 1
        if counter == distance:
            counter = 0
            Cloud(clouds)
        time.sleep(delay)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                db.close()
                running = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    skydiver.rect.x = 200
                elif event.key == pg.K_LEFT:
                    skydiver.rect.x = 10
                elif event.key == pg.K_DOWN:
                    skydiver.rect.y += 30
                elif event.key == pg.K_UP:
                    skydiver.rect.y -= 30

        screen.fill((115, 195, 225))
        draw_text(screen, str(scores), 18, WIDTH / 2, 10)

        skydivers.draw(screen)
        clouds.draw(screen)
        skydivers.update()
        clouds.update()

        pg.display.flip()
    pg.quit()
    clock.tick(FPS)


if __name__ == "__main__":
    main()


# add some animation to collide
