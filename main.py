import os
import sys
import sqlite3
import time
from random import choice
import pygame as pg


class Db:
    def __init__(self, db_name="users.sqlite3"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        '''создание таблицы, если ее не сущуствует'''
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                                login TEXT UNIQUE NOT NULL,
                                password TEXT UNIQUE NOT NULL,
                                scores REAL);''')

        self.connection.commit()  # сохранение изменений
    '''функция для входа в аккаунт'''

    def login(self, login, password):
        '''если аккаунт не существует, то создается новый'''
        self.cursor.execute(
            '''INSERT OR IGNORE INTO Users (login, password, scores)
            VALUES (?, ?, 0);''',
            (login, password))
        self.connection.commit()
        '''если пароль и логин совпадают'''
        if self.cursor.execute(
                "SELECT * FROM Users WHERE login = ? AND password = ?",
                (login, password)).fetchone() is not None:
            print("Login successful")
            return True

    def clear_achievements(self, login):
        try:
            print("Clearing achievements")
            self.cursor.execute(
                "UPDATE Users SET scores = ? WHERE login = ?",
                (0, login))
            self.connection.commit()
        except Exception:
            print("Error clearing achievements")

    '''функция для получения очков из БД'''

    def get_scores(self, login):
        try:
            return round(self.cursor.execute(
                "SELECT scores FROM Users WHERE login = ?",
                (login,)).fetchone()[0], 1)
        except Exception:
            return 0  # Если у пользователя нет очков, то возвращается 0
    '''функция для добавления результата в БД'''

    def add_result(self, scores, login):
        try:
            scores_ = self.get_scores(login)
            print(scores_)
            self.cursor.execute(
                "UPDATE Users SET scores = ?",
                (float(scores_) + float(scores),))
            self.connection.commit()
        except sqlite3.IntegrityError as message:
            print("Error!")
            raise SystemExit(message)
    '''закрытие БД'''

    def close(self):
        self.connection.close()


pg.init()  # инициализация pygame
scores_display = None
db = Db()  # создание объекта класса Db
scores = 0
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
FONT_ = 'z003'  # игровой шрифт


'''Класс для чекбокса'''


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
        '''объект чекбокса'''
        self.checkbox_obj = pg.Rect(self.x, self.y, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()
        '''переменные для проверки состояния чекбокса'''
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
    '''отрисовка чекбокса'''

    def render_checkbox(self):
        if self.checked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            pg.draw.circle(self.surface, self.cc, (self.x + 6, self.y + 6), 4)

        elif self.unchecked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
        self._draw_button_text()

    '''функции для проверки состояния чекбокса'''

    def is_checked(self):
        if self.checked is True:
            return True
        else:
            return False

    def handel_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.checkbox_obj.collidepoint(event.pos):
                self.checked = not self.checked

    def is_unchecked(self):
        if self.checked is False:
            return True
        else:
            return False


'''Класс для текстового поля'''


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        '''Если пользователь нажал на поле ввода'''
        if event.type == pg.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Смена текущего цвета
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
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        '''Поменять размер поля ввода при необходимости'''
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.color, self.rect, 2)


'''Функция для записи результатов'''


def write_result():
    global scores, login, level
    db.add_result(scores, login)
    db.close()


'''функция для загрузки изображений'''


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
    except pg.error as message:  # если файл не найден, то выводим ошибку
        print(f'Image {name} not found!')
        raise SystemExit(message)


'''функция для загрузки музыки'''


def load_music(name):
    fullname = os.path.join("data/music/", name)
    try:
        melody = pg.mixer.music.load(fullname)
        pg.mixer.music.play(-1)
        return melody
    except pg.error as message:  # если файл не найден, то выводим ошибку
        print(f'Melody {name} not found!')
        raise SystemExit(message)


SIZE = WIDTH, HEIGHT = 300, 700
FPS = 60
COLOR_INACTIVE = pg.Color(136, 138, 133)
COLOR_ACTIVE = pg.Color(0, 0, 0)
FONT = pg.font.Font(None, 32)
FONT_NAME = 'z003'  # шрифт для текста

screen = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
pg.display.set_icon(load_image("skydiver.png"))  # иконка игры


pg.display.set_caption("Skydiver")  # название игры

'''функция для остановки программы'''


def terminate():
    pg.quit()
    sys.exit()


'''функция для отрисовки экрана проигрыша'''


def end_screen():
    global running
    write_result()
    intro_text = ['Game over!',
                  f'Your score: {scores_display}',
                  'Press "ESC" to exit']
    screen.fill((115, 195, 225))
    font = FONT_
    text_coord = 280
    for line in intro_text:
        string_rendered = font.render(line, 1, pg.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 80
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


'''функция для отрисовки экрана победы'''


def victory_screen():
    global running
    screen.fill((115, 195, 225))
    write_result()
    intro_text = [f"U've passed the {level} level!",
                  'Press "ESC" to exit']

    font = FONT_
    text_coord = 280
    for line in intro_text:
        string_rendered = font.render(line, 1, pg.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
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
chkbox2 = Checkbox(screen, WIDTH - 20, 270)
'''функция для отрисовки экрана входа'''


def start_screen():
    global level, running, FONT_
    cursor_image = load_image("cursor.png")
    cursor = pg.sprite.Sprite(other_spriites)
    cursor.image = cursor_image
    cursor.rect = cursor.image.get_rect()
    pg.mouse.set_visible(False)
    input_box1 = InputBox(95, 30, 140, 32)
    input_box2 = InputBox(95, 100, 140, 32)
    input_box3 = InputBox(95, 170, 140, 32)
    input_boxes = [input_box1, input_box2, input_box3]
    arr = list()
    FONT_ = pg.font.SysFont(FONT_, 24)
    text2 = FONT_.render("Password", True,
                         (0, 0, 0))
    text1 = FONT_.render("Login", True,
                         (0, 0, 0))
    text3 = FONT_.render("Level", True,
                         (0, 0, 0))
    text4 = FONT_.render("Music", True, (0, 0, 0))
    text5 = FONT_.render("Clear achievements", True, (0, 0, 0))

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
            if event.type == pg.MOUSEMOTION:
                cursor.rect.topleft = event.pos
            chkbox.handel_event(event)
            chkbox2.handel_event(event)
        for box in input_boxes:
            box.update()
        screen.fill((115, 195, 225))
        for box in input_boxes:
            box.draw(screen)
        screen.blit(text2, (5, 105))
        screen.blit(text1, (5, 35))
        screen.blit(text3, (5, 175))
        screen.blit(text4, (WIDTH - 90, 235))
        screen.blit(text5, (WIDTH - 197, 265))

        chkbox.render_checkbox()
        chkbox2.render_checkbox()
        if pg.mouse.get_focused():
            other_spriites.draw(screen)
        pg.display.flip()
        clock.tick(FPS)


'''класс Skydiver'а'''


class Skydiver(pg.sprite.Sprite):
    image = load_image("skydiver.png")  # загрузка изображения

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


skydivers = pg.sprite.Group()  # создать группу спрайтов
skydiver = Skydiver(skydivers)  # добавиить спрайт в группу

'''класс препятствия'''


class Obstacle(pg.sprite.Sprite):
    images = ["cloud.png", "cloudO.png", "bird.png"]
    POSITIONS_X = [10, WIDTH - 80]

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
        global scores, level, scores_display
        if not pg.sprite.collide_mask(self, skydiver):
            self.rect.y -= self.speedy
        elif pg.sprite.spritecollideany(self, horizontal_borders):
            self.kill()
        else:

            if self.name == "cloud.png":
                if level == 2:
                    scores += 0.2
                    scores_display += 0.2
                else:
                    scores += 0.1
                    scores_display += 0.1
                scores = round(scores, 1)
                scores_display = round(scores_display, 1)
                self.kill()
            if self.name == "cloudO.png":
                scores += 0.5
                scores_display += 0.5
                scores = round(scores, 1)
                scores_display = round(scores_display, 1)
                self.kill()
            if self.name == "bird.png":
                self.kill()
                end_screen()


horizontal_borders = pg.sprite.Group()  # создать группу спрайтов
borders = pg.sprite.Group()  # добавить спрайт в группу
vertical_borders = pg.sprite.Group()  # создать группу спрайтов


class Border(pg.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pg.Surface([1, y2 - y1])
            self.rect = pg.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pg.Surface([x2 - x1, 1])
            self.rect = pg.Rect(x1, y1, x2 - x1, 1)


font_name = pg.font.match_font(FONT_)

'''функция для отрисовки текста'''


def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, (203, 0, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


melody_name = 'melody.mp3'  # название файла с мелодией

other_spriites = pg.sprite.Group()  # создать группу спрайтов


def main():
    global running, distance, level, delay, time_, scores, login, \
        scores_display

    color = None
    start_screen()  # вызов стартового экрана
    if chkbox.is_checked():
        load_music(melody_name)  # загрузка мелодии
    if chkbox2.is_checked():
        print("Achievements cleared")
        db.clear_achievements(login)
    scores_display = db.get_scores(login)  # получение очков из базы данных

    if level == 1:
        '''правила для I уровня'''
        distance = 170
        delay = 0.004
        color = 114, 159, 207
    elif level == 2:
        '''правила для II уровня'''
        distance = 170
        delay = 0.002
        color = 32, 74, 135
    clouds = pg.sprite.Group()
    # pg.mouse.set_visible(False)
    counter = distance - 1
    Border(5, 5, WIDTH - 5, 5)
    Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    Border(5, 5, 5, HEIGHT - 5)
    Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
    '''главный игровойй цикл'''
    while True:
        if not running:
            break
        if scores_display >= 100:
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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    skydiver.rect.x = WIDTH - 63
                if event.key == pg.K_LEFT:
                    skydiver.rect.x = 10
                if event.key == pg.K_DOWN:
                    skydiver.rect.y += 30
                if event.key == pg.K_UP:
                    skydiver.rect.y -= 30
        screen.fill(color)
        draw_text(screen, str(scores_display), 22, WIDTH / 2, 10)

        skydivers.draw(screen)
        clouds.draw(screen)
        skydivers.update()
        clouds.update()

        pg.display.flip()
    pg.quit()
    clock.tick(FPS)


if __name__ == "__main__":
    main()
    terminate()  # закрыть программу
