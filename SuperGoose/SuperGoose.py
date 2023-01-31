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
player_group = pygame.sprite.Group() # КАРТИНКИ ФОНА НЕ КОНЕЧНЫЙ ВАРИАНТ
camera_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
ENEMY_EVENT_TYPE = 30
player = None
count = 0
pygame.mixer.music.load('music/start_window.mp3')
pygame.mixer.music.play(-1)
fl_pause = False
vol = 1.0
levels_passed = [0 for i in range(6)]


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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


tile_images = {
    'empty': pygame.transform.scale(load_image('ground.png'), (50, 50)),
    'wall': pygame.transform.scale(load_image('wall.png'), (50, 50)),
    'cup': pygame.transform.scale(load_image('cup.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('goose.png'), (50, 50))


def terminate():
    pygame.quit()
    sys.exit()


def back():
    objects.clear()
    start_screen()


def start_screen():
    global fl_pause, vol
    #clock = pygame.time.Clock()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('supergoose.png'), (width, height))
    screen.blit(fon, (0, 0))
    #effects = AnimatedSprite(load_image('8.png'), 1, 4, 10, 10)
    Button(60, 200, 400, 75, 'Уровни', levels)
    Button(60, 290, 195, 75, 'SuperGoose', SuperGoose)
    Button(265, 290, 195, 75, 'Справка', help)
    Button(60, 380, 195, 75, 'Прогресс', progress)
    Button(265, 380, 195, 75, 'Магазин', shop)
    Button(420, 5, 75, 50, 'Set', settings)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
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
        self.fillColors = {'normal': (0, 162, 232), 'hover': (237, 28, 36), 'pressed': (0, 0, 255)}
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
    global fl_pause, vol
    objects.clear()
    width = 506
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('2goose.png'), (width, height))
    screen.blit(fon, (0, 0))
    rules = ["          Уровни", "", "Выберите уровень:"]
    font = pygame.font.SysFont('Times New Roman', 60)
    text_coord = 20
    Button(15, 280, 155, 75, 'Уровень 1', labyrinth_level)
    Button(175, 280, 155, 75, 'Уровень 2', fly_level)
    Button(335, 280, 155, 75, 'Уровень 3', fly_level_enemies)
    Button(15, 365, 155, 75, 'Уровень 4', labyrinth_level)
    Button(175, 365, 155, 75, 'Уровень 5', labyrinth_level)
    Button(335, 365, 155, 75, 'Уровень 6', labyrinth_level)
    Button(10, 10, 100, 50, 'Назад', back)
    for line in rules:
        line_rendered = font.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def labyrinth_level():
    global fl_pause, vol
    objects.clear()
    screen = pygame.display.set_mode((1350, 850))
    player, enemy, level_x, level_y = generate_level(load_level('labyrinth_level.txt'))
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 500)
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
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
            if event.type == ENEMY_EVENT_TYPE:
                move_enemy(enemy, player)
        if player.rect.x == 1250 and player.rect.y == 750:
            print('Поздравляем, вы прошли первый уровень!')
            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
            enemy.kill()
            player.kill()
            if levels_passed[0] == 0:
                count += 1
                levels_passed[0] = 1
            back()
            return
        if player.rect == enemy.rect:
            print('Вы проиграли :(')
            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
            enemy.kill()
            player.kill()
            back()
            return
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def find_path_step(start, target):
    INF = 1000
    x, y = start
    distance = [[INF] * (screen.get_width() // STEP) for i in range(screen.get_height() // STEP)]
    distance[y][x] = 0
    prev = [[None] * (screen.get_width() // STEP) for i in range(screen.get_height() // STEP)]
    queue = [(x, y)]
    while queue:
        x, y = queue.pop(0)
        for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
            next_x, next_y = x + dx, y + dy
            if 0 <= next_x < screen.get_width() // STEP and\
                    0 < next_y < screen.get_height() // STEP and\
                    is_free(next_x, next_y) and distance[next_y][next_x] == INF:
                distance[next_y][next_x] = distance[y][x] + 1
                prev[next_y][next_x] = (x, y)
                queue.append((next_x, next_y))
    x, y = target
    if distance[y][x] == INF or start == target:
        return start
    while prev[y][x] != start:
        x, y = prev[y][x]
    return x * STEP, y * STEP


def move_enemy(enemy, player):
    past_x, past_y = enemy.rect.x, enemy.rect.y
    next_position = find_path_step((enemy.rect.x // STEP, enemy.rect.y // STEP),
                                   (player.rect.x // STEP, player.rect.y // STEP))
    enemy.rect.x, enemy.rect.y = next_position
    if past_x - enemy.rect.x < 0:
        enemy.update_frame('right')
    elif past_x - enemy.rect.x > 0:
        enemy.update_frame('left')
    elif past_y - enemy.rect.y < 0:
        enemy.update_frame('down')
    elif past_y - enemy.rect.y > 0:
        enemy.update_frame('up')


def is_free(x, y):
    if load_level('labyrinth_level.txt')[y][x] != '#':
        return True
    return False


def fly_level():
    global fl_pause, vol
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    camera = Camera()
    objects.clear()
    screen = pygame.display.set_mode((500, 350))
    player, enemy, level_x, level_y = generate_level(load_level('fly_level.txt'))
    cam = Player(0, 150, True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.rect.x -= STEP
                    if pygame.sprite.spritecollideany(player, box_group):
                        end_game()
                if event.key == pygame.K_RIGHT:
                    player.rect.x += STEP
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
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
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


def end_game():
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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.enemy_image = AnimatedSprite(load_image('wolf.png'), 3, 4, 0, 0)
        self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update_frame(self, direction):
        if direction == 'right':
            self.enemy_image.cur_frame = 6 + self.enemy_image.cur_frame % 3 + 1
            self.enemy_image.image = self.enemy_image.frames[self.enemy_image.cur_frame - 1]
            self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))
        elif direction == 'left':
            self.enemy_image.cur_frame = 3 + self.enemy_image.cur_frame % 3 + 1
            self.enemy_image.image = self.enemy_image.frames[self.enemy_image.cur_frame - 1]
            self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))
        elif direction == 'down':
            self.enemy_image.cur_frame = 0 + self.enemy_image.cur_frame % 3 + 1
            self.enemy_image.image = self.enemy_image.frames[self.enemy_image.cur_frame - 1]
            self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))
        elif direction == 'up':
            self.enemy_image.cur_frame = 9 + self.enemy_image.cur_frame % 3 + 1
            self.enemy_image.image = self.enemy_image.frames[self.enemy_image.cur_frame - 1]
            self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))


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
    new_player, new_enemy, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '*':
                Tile('cup', x, y)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                new_enemy = Enemy(x, y)
    return new_player, new_enemy, x, y


def SuperGoose():
    global fl_pause, vol
    objects.clear()
    width = 700
    height = 600
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('goose2.png'), (width, height))
    screen.blit(fon, (0, 0))
    with open('output/Goose.txt', 'r') as file:
        lines = file.readlines()
    name = ["                     SuperGoose", ""]
    font = pygame.font.SysFont('Times New Roman', 30)
    font1 = pygame.font.SysFont('Times New Roman', 45)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    for line in name:
        line_rendered = font1.render(line, 1, (0, 0, 0))
        line_rect = line_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = 10
        text_coord += line_rect.height
        screen.blit(line_rendered, line_rect)
    for line in lines:
        line_rendered = font.render(line, 1, (237, 28, 36))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def help():
    global fl_pause, vol
    objects.clear()
    width = 605
    height = 600
    screen = pygame.display.set_mode((605, 600))
    fon = pygame.transform.scale(load_image('superman.png'), (width, height))
    screen.blit(fon, (0, 0))
    with open('output/help1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    name = ["          Справка", ""]
    font = pygame.font.SysFont('Times New Roman', 60)
    font1 = pygame.font.SysFont('Times New Roman', 30)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    Button(410, 10, 185, 50, 'Страница 2', help_page_2)
    for line in name:
        line_rendered = font.render(line, 1, (237, 28, 36))
        line_rect = line_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = 10
        text_coord += line_rect.height
        screen.blit(line_rendered, line_rect)
    for line in lines:
        line_rendered = font1.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def help_page_2():
    global fl_pause, vol
    objects.clear()
    width = 605
    height = 600
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    with open('output/help2.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    font = pygame.font.SysFont('Times New Roman', 30)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    for line in lines:
        line_rendered = font.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def progress():
    global count, fl_pause, vol
    objects.clear()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('sgoose.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["        Прогресс", ""]
    text = ['Твой прогресс:', f'                 {count} из 6 уровней!']
    if count == 6:
        text.append('Молодец!')
        text.append('Ты прошёл игру!!!')
        count = 0
    font = pygame.font.SysFont('Times New Roman', 63)
    font1 = pygame.font.SysFont('Times New Roman', 45)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    for line in name:
        line_rendered = font.render(line, 1, (0, 0, 0))
        line_rect = line_rendered.get_rect()
        text_coord += 10
        line_rect.top = text_coord
        line_rect.x = 10
        text_coord += line_rect.height
        screen.blit(line_rendered, line_rect)
    for line in text:
        line_rendered = font1.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def settings():
    global fl_pause, vol
    objects.clear()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('superman.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["       Настройки", "", "Настройки скоро", "появятся"]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    for line in name:
        line_rendered = font.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


def shop():
    global fl_pause, vol
    objects.clear()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('sgoose.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["        Магазин", "", "Магазин скоро", "появится!"]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    for line in name:
        line_rendered = font.render(line, 1, (0, 0, 0))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fl_pause = not fl_pause
                    if fl_pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_MINUS:
                    vol -= 0.1
                    pygame.mixer.music.set_volume(vol)
                elif event.key == pygame.K_EQUALS:
                    vol += 0.1
                    pygame.mixer.music.set_volume(vol)
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    pygame.display.flip()
    clock.tick(FPS)
