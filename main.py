# Standard library imports
import os
import sys
import sqlite3
import time
from random import choice

# Third-party imports
import pygame as pg


pg.init()

scores = int()
time_ = None
running = True
level = None
distance = None
delay = None
COLOR_INACTIVE = pg.Color(136, 138, 133)
COLOR_ACTIVE = pg.Color(0, 0, 0)
FONT = pg.font.Font(None, 32)
login = None
password = None
font_ = 'z003'


class Db:
    def __init__(self, db_name="users.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                                login TEXT UNIQUE NOT NULL,
                                password TEXT UNIQUE NOT NULL,
                                scores REAL);''')

        self.connection.commit()

    def login(self, login, password):
        self.cursor.execute(
            "INSERT OR IGNORE INTO Users (login, password, scores) VALUES (?, ?, 0);",
            (login, password))
        self.connection.commit()
        if self.cursor.execute(
                "SELECT * FROM Users WHERE login = ? AND password = ?",
                (login, password)).fetchone() != None:
            print("Login successful")
            return True

    def add_result(self, scores, login):
        try:
            scores_ = self.cursor.execute(
                "SELECT scores FROM Users WHERE login = ?", (login,)).fetchone()
            print(scores_)
            self.cursor.execute(
                "UPDATE Users SET scores = ?",
                (float(scores_[0]) + float(scores),))
            self.connection.commit()
        except sqlite3.IntegrityError as message:
            print("Error!")
            raise SystemExit(message)

    def close(self):
        self.connection.close()


db = Db()


class Checkbox:
    def __init__(self, surface, x, y, color=(230, 230, 230), caption="",
                 outline_color=(0, 0, 0),
                 check_color=(0, 0, 0), font_size=22, font_color=(0, 0, 0),
                 text_offset=(28, 1)):
        self.surface = surface
        self.x = x
        self.y = y
        self.color = color
        self.caption = caption
        self.oc = outline_color
        self.cc = check_color
        self.fs = font_size
        self.fc = font_color
        self.to = text_offset
        # checkbox object
        self.checkbox_obj = pg.Rect(self.x, self.y, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()
        # variables to test the different states of the checkbox
        self.checked = False
        self.active = False
        self.unchecked = True
        self.click = False
        self.unactive = False

    def _draw_button_text(self):
        self.font = pg.font.Font(None, self.fs)
        self.font_surf = self.font.render(self.caption, True, self.fc)
        w, h = self.font.size(self.caption)
        self.font_pos = (self.x + 12 / 2 - w / 2 +
                         self.to[0], self.y + 12 / 2 - h / 2 + self.to[1])
        self.surface.blit(self.font_surf, self.font_pos)

    def render_checkbox(self):
        if self.checked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            pg.draw.circle(self.surface, self.cc, (self.x + 6, self.y + 6), 4)

        elif self.unchecked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
        self._draw_button_text()

    def _update(self, event_object):
        x, y = event_object.pos
        # self.x, self.y, 12, 12
        px, py, w, h = self.checkbox_obj  # getting check box dimensions
        if px < x < px + w and px < x < px + w:
            self.active = True
        else:
            self.active = False

    def _mouse_up(self):
        if not self.unactive:
            if self.active and not self.checked and self.click:
                self.checked = True

            elif self.checked:
                self.checked = False
                self.unchecked = True

            if self.click is True and self.active is False:
                if self.checked:
                    self.checked = True
                if self.unchecked:
                    self.unchecked = True
                self.active = False

    def update_checkbox(self, event_object):
        if event_object.type == pg.MOUSEBUTTONDOWN:
            self.click = True
        if event_object.type == pg.MOUSEBUTTONUP:
            self._mouse_up()
            self.unactive = True
        if event_object.type == pg.MOUSEMOTION:
            self._update(event_object)

    def is_checked(self):
        if self.checked is True:
            return True
        else:
            return False

    def is_unchecked(self):
        if self.checked is False:
            return True
        else:
            return False


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
                    self.active = False
                    return self.text
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
    global scores, login, level

    db.add_result(scores, login)
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
FPS = 60
COLOR_INACTIVE = pg.Color(136, 138, 133)
COLOR_ACTIVE = pg.Color(0, 0, 0)
FONT = pg.font.Font(None, 32)
FONT_NAME = 'z003'

screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
pg.display.set_icon(load_image("skydiver.png"))


pg.display.set_caption("Skydiver")


def terminate():
    pg.quit()
    sys.exit()


def end_screen():
    global running
    write_result()
    intro_text = ['Game over!',
                  f'Your score: {scores}',
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


chkbox = Checkbox(screen, WIDTH - 20, 240)


def start_screen():
    global level, running, font_
    input_box1 = InputBox(95, 30, 140, 32)
    input_box2 = InputBox(95, 100, 140, 32)
    input_box3 = InputBox(95, 170, 140, 32)
    input_boxes = [input_box1, input_box2, input_box3]
    arr = list()
    font_ = pg.font.SysFont(font_, 24)
    text2 = font_.render("Password", True,
                         (0, 0, 0))
    text1 = font_.render("Login", True,
                         (0, 0, 0))
    text3 = font_.render("Level", True,
                         (0, 0, 0))
    text4 = font_.render("Music", True, (0, 0, 0))

    while True:
        global login, password
        if len(arr) == 3:
            login = arr[0]
            password = arr[1]
            if db.login(login, password):
                level = int(arr[2])
                return
            else:
                arr = list()

        for event in pg.event.get():
            for box in input_boxes:
                el = box.handle_event(event)
                if el:
                    arr.append(el)
            chkbox.update_checkbox(event)
        for box in input_boxes:
            box.update()
        screen.fill((115, 195, 225))
        for box in input_boxes:
            box.draw(screen)
        screen.blit(text2, (5, 105))
        screen.blit(text1, (5, 35))
        screen.blit(text3, (5, 175))
        screen.blit(text4, (WIDTH - 90, 235))
        chkbox.render_checkbox()
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


class Obstacle(pg.sprite.Sprite):
    images = ["cloud.png", "cloudO.png", "bird.png"]
    POSITIONS_X = [10, 200]

    def __init__(self, *group):
        super().__init__(*group)
        self.name = choice(Obstacle.images)
        self.image = load_image(self.name)
        self.rect = self.image.get_rect()
        self.rect.x = choice(Obstacle.POSITIONS_X)
        self.rect.y = 700
        self.speedy = 1
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        global scores, level
        if not pg.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        elif pg.sprite.spritecollideany(self, horizontal_borders):
            self.kill()
        else:
            if self.name == "cloud.png":
                if level == 3:
                    scores += 0.3
                elif level == 2:
                    scores += 0.2
                else:
                    scores += 0.1
                scores = round(scores, 1)
                self.kill()
            if self.name == "cloudO.png":
                scores += 0.5
                scores = round(scores, 1)
                self.kill()
            if self.name == "bird.png":
                self.kill()
                end_screen()


horizontal_borders = pg.sprite.Group()
borders = pg.sprite.Group()


class Border(pg.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        self.add(horizontal_borders)
        self.image = pg.Surface([x2 - x1, 1])
        self.rect = pg.Rect(x1, y1, x2 - x1, 1)


font_name = pg.font.match_font(font_)


def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


melody_name = 'melody.mp3'


def main():
    global running, distance, level, delay, time_, scores
    color = None
    start_screen()
    if chkbox.is_checked():
        load_music(melody_name)
    if level == 1:
        distance = 170
        delay = 0.004
        color = 114, 159, 207
    elif level == 2:
        distance = 170
        delay = 0.002
        color = 52, 101, 164
    elif level == 3:
        distance = 150
        delay = 0.002
        color = 32, 74, 135
    clouds = pg.sprite.Group()
    # pg.mouse.set_visible(False)
    counter = distance - 1
    Border(5, 5, WIDTH - 5, 5)
    Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    Border(5, 5, 5, HEIGHT - 5)
    Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)

    while True:
        if not running:
            break
        if scores >= 100:
            victory_screen()
        counter += 1
        if counter == distance:
            counter = 0
            Obstacle(clouds)
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

        screen.fill(color)
        draw_text(screen, str(scores), 22, WIDTH / 2, 10)

        skydivers.draw(screen)
        clouds.draw(screen)
        skydivers.update()
        clouds.update()

        pg.display.flip()
    pg.quit()
    clock.tick(FPS)


if __name__ == "__main__":
    main()
    pg.quit()
