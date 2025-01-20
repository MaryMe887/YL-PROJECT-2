import os
import pygame, sys

pygame.init()
FPS = 50
clock = pygame.time.Clock()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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
    return image


def game_exit():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["COP CAT", "",
                  "Начать игру",
                  "Настройки"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('purple'))
        intro_rect = string_rendered.get_rect()
        text_coord += 50
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                screen.fill((0, 0, 0))
                all_sprites.draw(screen)
                pygame.display.flip()
                return generate_level(load_level('map.txt'))
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_width = tile_height = 50
tile_images = {
    'rock': pygame.transform.scale(load_image('rock.png'), (30, 30)),
    'empty': pygame.transform.scale(load_image('grass.png'), (tile_width, tile_height))
}
player_image = pygame.transform.scale(load_image('cop.png'), (40, 50))


tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, dx, dy):
        new_x = self.rect.x + dx * tile_width
        new_y = self.rect.y + dy * tile_height
        if 0 > new_x >= width and 0 > new_y >= height:
            return
        for tile in tiles_group:
            if tile.image == tile_images['wall']:
                if tile.rect.colliderect(pygame.Rect(new_x - 15, new_y - 5,
                                                     tile_width, tile_height)):
                    return
        self.rect.x = new_x
        self.rect.y = new_y


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('empty', x, y)
                Tile('rock', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


class Game:
    def __init__(self):
        pygame.display.set_caption("Cat Cop")
        start_screen()
        level_map = load_level('map.txt')
        new_level = generate_level(level_map)
        player = new_level[0]
        # screen = pygame.display.set_mode((new_level[1] * tile_width, new_level[2]))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0)
                    elif event.key == pygame.K_LEFT:
                        player.move(-1, 0)
            pygame.display.flip()
            clock.tick(FPS)

            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            player_group.draw(screen)
            clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    Game()
