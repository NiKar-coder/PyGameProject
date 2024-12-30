import pygame
import os
pygame.init()
size = width, height = 300, 700
screen = pygame.display.set_mode(size)


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
        self.rect.x = 0
        self.rect.y = 0


def main():


    pygame.display.set_icon(load_image("skydiver.png"))
    clock = pygame.time.Clock()
    load_music('melody.mp3')
    pygame.display.set_caption("Skydiver")
    all_sprites = pygame.sprite.Group()
    skydiver = Skydiver(all_sprites)

    pygame.mouse.set_visible(False)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    skydiver.rect.x = 200
                elif event.key == pygame.K_LEFT:
                    skydiver.rect.x = 1
        screen.fill((115, 195, 225))
        all_sprites.draw(screen)

        pygame.display.flip()
    pygame.quit()
    clock.tick(60)


if __name__ == "__main__":
    main()
