import pygame
import os
import sys
import random


pygame.init()
size = width, height = 500, 500
FPS = 50
STEP = 50
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
objects = []
font = pygame.font.SysFont('Arial', 40)
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
camera_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
player = None


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с рисунком "{fullname}" не найден!')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is None:
        image.convert_alpha()
    else:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


tile_images = {
    'empty': pygame.transform.scale(load_image('ground.png'), (50, 50)),
    'wall': pygame.transform.scale(load_image('wall.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('goose.png'), (50, 50))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    rules = ["      SuperGoosе", ""]
    screen.fill((0, 100, 255))
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 50
    Button(60, 200, 400, 75, 'Уровни', levels)
    Button(60, 290, 195, 75, 'SuperGoose', SuperGoose)
    Button(265, 290, 195, 75, 'Справка', help)
    Button(60, 380, 195, 75, 'Прогресс', progress)
    Button(265, 380, 195, 75, 'Магазин', shop)
    for line in rules:
        line_rendered = font.render(line, 1, (0, 255, 0))
        line_rect = line_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = 10
        text_coord += line_rect.height
        screen.blit(line_rendered, line_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None,
                onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False
        self.fillColors = {'normal': (0, 255, 0), 'hover': (175, 0, 0), 'pressed': (0, 0, 255)}
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        objects.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2])
        screen.blit(self.buttonSurface, self.buttonRect)


def levels():
    objects.clear()
    rules = [""]
    screen.fill((0, 100, 255))
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 50
    Button(60, 100, 400, 75, 'Уровень 1', labyrinth_level)
    Button(60, 190, 400, 75, 'Уровень 2', fly_level)
    Button(60, 280, 400, 75, 'Уровень 3', fly_level_enemies)
    for line in rules:
        line_rendered = font.render(line, 1, (0, 255, 0))
        line_rect = line_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = 10
        text_coord += line_rect.height
        screen.blit(line_rendered, line_rect)


def labyrinth_level():
    objects.clear()
    screen = pygame.display.set_mode((1350, 850))
    player, level_x, level_y = generate_level(load_level('labyrinth_level.txt'))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.rect.x -= STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.rect.x += STEP
                if event.key == pygame.K_RIGHT:
                    player.rect.x += STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.rect.x -= STEP
                if event.key == pygame.K_DOWN:
                    player.rect.y += STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.rect.y -= STEP
                if event.key == pygame.K_UP:
                    player.rect.y -= STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.rect.y += STEP
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def fly_level():
    camera = Camera()
    objects.clear()
    screen = pygame.display.set_mode((500, 350))
    player, level_x, level_y = generate_level(load_level('fly_level.txt'))
    cam = Player(0, 150, True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.rect.x -= STEP // 2
                    if pygame.sprite.spritecollideany(player, box_group):
                        end_game()
                if event.key == pygame.K_RIGHT:
                    player.rect.x += STEP // 2
                    if pygame.sprite.spritecollideany(player, box_group):
                        end_game()
                if event.key == pygame.K_DOWN:
                    player.rect.y += STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        end_game()
                if event.key == pygame.K_UP:
                    player.rect.y -= STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        end_game()
            if not (cam.rect.x - 250 <= player.rect.x <= cam.rect.x + 250):
                end_game()
        player.rect.x += 1
        cam.rect.x += 1
        camera.update(cam)
        for sprite in all_sprites:
            camera.apply(sprite, level_x, level_y)
        screen.fill((0, 0, 0))
        camera_group.draw(screen)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def fly_level_enemies():
    pass


def load_level(level_name):
    level_name = 'data/levels/' + level_name
    with open(level_name, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'wall':
            self.add(box_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, camera=False):
        if camera:
            super().__init__(camera_group, all_sprites)
        else:
            super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj, level_x, level_y):
        obj.rect.x += self.dx
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (level_x + 1) * obj.rect.width
        if obj.rect.x >= obj.rect.width * level_x:
            obj.rect.x -= (level_x + 1) * obj.rect.width

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def end_game():
    print('Игра окончена')
    terminate()


def SuperGoose():
    print('История о гусе скоро появится!')


def help():
    print('Помощь скоро прибудет!')


def progress():
    print('Прогресс скоро появится!')


def shop():
    print('Магазин скоро откроется!')


start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    pygame.display.flip()
    clock.tick(FPS)
