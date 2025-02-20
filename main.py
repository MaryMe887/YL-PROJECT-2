import os
import pygame
import sys


# важные переменные, которые понадобятся ниже
pygame.init()
FPS = 60
clock = pygame.time.Clock()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
weapons = {'gun': {'damage': 10, 'cooldown': 50, 'graphic': 'gun_image'}}
enemies = {'rat': {'health': 60, 'damage': 5, 'image': 'rat.png',
                   'speed': 2, 'attack_radius': 30, 'notice_radius': 50, 'size': (100, 200)}}


def load_image(name, colorkey=None):
    '''загрузка изображений'''
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
    '''выход из игры'''
    pygame.quit()
    sys.exit()


def start_screen():
    '''начальный экран'''
    intro_text = ["COP CAT",
                  "Начать игру",
                  "Настройки",
                  "Выход"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    text_coord = 50
    font = pygame.font.Font('joystix.ttf', 20)
    # отображение 'кнопок'
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color((66, 9, 99)))
        intro_rect = string_rendered.get_rect()
        text_coord += 50
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    # смотрим, куда игрок нажал
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 195 >= event.pos[0] >= 10 and 198 >= event.pos[1] >= 174:
                    return
                if 95 >= event.pos[0] >= 10 and 346 >= event.pos[1] >= 322:
                    return game_exit()
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    '''загрузка уровня'''
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# переменные для самой игры
tile_width = tile_height = 50
tile_images = {
    'rock': pygame.transform.scale(load_image('rock.png'), (tile_width, tile_height)),
    'empty': pygame.transform.scale(load_image('grass.png'), (tile_width, tile_height))
}
player_image = pygame.transform.scale(load_image('cop.png'), (80, 100))

# группы спрайтов
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    '''класс тайлов'''
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    '''класс игрока'''
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image.subsurface((0, 50, 80, 50))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        # переменные для анимации моргания
        self.blinking = False
        self.blink_timer = 0
        self.blink_interval = 2000
        # статы
        self.stats = {'hp': 100, 'attack': 10, 'speed': 10}
        self.current_hp = 100

    def move(self, dx, dy):
        # метод движения
        speed = self.stats['speed']
        new_x = self.rect.x + dx * speed
        new_y = self.rect.y + dy * speed
        if new_x < 0 or new_x > width - self.rect.width:
            return
        if new_y < 0 or new_y > height - self.rect.height:
            return
        for tile in tiles_group:
            # если столкнулся с преградой, не двигаемся
            if tile.image == tile_images['rock']:
                if pygame.sprite.collide_mask(self, tile):
                    return
        self.rect.x = new_x
        self.rect.y = new_y
        print(self.rect.x, self.rect.y)

    def blink(self):
        # анимация моргания
        current_time = pygame.time.get_ticks()
        if current_time - self.blink_timer >= self.blink_interval:
            if self.blinking:
                self.image = player_image.subsurface((0, 50, 80, 50))
            else:
                self.image = player_image.subsurface((0, 0, 80, 50))

            self.blinking = not self.blinking
            self.blink_timer = current_time

    def shoot(self):
        mouse_pos = pygame.mouse.get_pos()
        direction = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        distance = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
        if distance > 0:
            direction = (direction[0] / distance, direction[1] / distance)  # Нормализуем вектор
        Bullet(self.rect.center, direction)


class UI:
    '''класс отображения статов'''
    def __init__(self, player):
        # пока тут только самое важное - хп
        self.health_bar = pygame.Rect(10, 10, player.current_hp * 2, 20)

    def show_bar(self, player):
        pygame.draw.rect(screen, '#222222', pygame.Rect(10, 10, player.stats['hp'] * 2, 20))
        pygame.draw.rect(screen, 'red', self.health_bar)


class Bullet(pygame.sprite.Sprite):
    '''класс пули'''
    def __init__(self, pos, direction):
        super().__init__(all_sprites)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
        self.direction = direction
        while True:
            self.update()

    def update(self):
        new_x = self.direction[0] * self.speed
        new_y = self.direction[1] * self.speed
        # Удаление пули, если она выходит за пределы экрана
        if new_x < 0 or new_x > width or new_y < 0 or new_y > height:
            self.kill()
        self.rect = self.rect.move(new_x, new_y)


class Enemy(pygame.sprite.Sprite):
    '''класс противников'''
    def __init__(self, name, pos):
        super().__init__(enemy_group, all_sprites)
        self.image = pygame.transform.scale(load_image(enemies[name]['image']), enemies[name]['size'])
        self.rect = self.image.get_rect().move(
            tile_width * pos[0] + 15, tile_height * pos[1] + 5)
        self.hp = enemies[name]['health']
        self.state = 'idle'
        self.speed = enemies[name]['speed']
        self.attack_damage = enemies[name]['damage']
        self.attack_radius = enemies[name]['attack_radius']
        self.notice_radius = enemies[name]['notice_radius']
        print('Новый противник')

    def get_distance(self, player_pos):
        '''Вычисление расстояния до игрока'''
        return ((self.rect.centerx - player_pos[0]) ** 2 + (self.rect.centery - player_pos[1]) ** 2) ** 0.5

    def check_player(self, player):
        '''Проверка состояния врага относительно игрока'''
        distance = self.get_distance((player.rect.x, player.rect.y))
        # Если игрок в пределах радиуса заметности, приближаемся
        if distance <= self.notice_radius:
            self.state = 'approach'
        else:
            self.state = 'idle'

    def approach(self, player):
        '''Приближение к игроку'''
        distance = self.get_distance(player.rect.center)

        if distance > self.attack_radius:  # Только если враг не в атакующей позиции
            # вектор направления к игроку
            dx = (player.rect.centerx - self.rect.centerx)
            dy = (player.rect.centery - self.rect.centery)
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:  # Для избежания деления на ноль
                dx /= length
                dy /= length

            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def update(self, player):
        '''Обновление состояния врага на основе положения игрока'''
        self.check_player(player)
        if self.state == 'approach':
            self.approach(player)  # Приближаемся к игроку


def generate_level(level):
    '''генерация уровня'''
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
    Enemy('rat', (4, 4))
    return new_player, x * tile_width, y * tile_height


class Camera:
    '''класс камеры'''
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        # изменение координат всех объектов для отображения
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        # отображение относильно объекта target
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Game:
    '''сама игра'''
    def __init__(self):
        pygame.display.set_caption("Cat Cop")
        start_screen()
        # pygame.mixer.music.load('background.mp3')
        # pygame.mixer.music.play()
        level_map = load_level('map.txt')
        new_level = generate_level(level_map)
        player, width, height = new_level
        screen = pygame.display.set_mode((width, height))
        camera = Camera()
        running = True
        # управление
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        player.move(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        player.move(0, 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.move(1, 0)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        player.move(-1, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        player.shoot()
                        print('пау')
            pygame.display.flip()
            clock.tick(FPS)
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            screen.fill((0, 0, 0))
            ui = UI(player)
            tiles_group.draw(screen)
            player_group.draw(screen)
            all_sprites.draw(screen)
            for enemy in enemy_group:
                enemy.update(player)
            ui.show_bar(player)
            clock.tick(FPS)
            player.blink()
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    Game()
