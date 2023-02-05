import pygame
import os
import sys
import gc

# создаём главное окно, основные переменные, группы спрайтов и константы
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
enemy_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
ENEMY_EVENT_TYPE = 30
player = None
enemy = None
enemies = None
count = 0
pygame.mixer.music.load('music/start_window.mp3')
pygame.mixer.music.play(-1)
fl_pause = False
vol = 1.0
levels_passed = [0 for i in range(6)]
coin = 0
not_press = False
not_press1 = False
not_press2 = False
not_press3 = False
not_press4 = False
not_choose = False
not_choose1 = False
not_choose2 = False
not_choose3 = False
not_choose4 = False


# метод для загрузки  изображения
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


# класс анимации
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


# добавляем нужные картинки
tile_images = {
    'empty': pygame.transform.scale(load_image('ground.png'), (50, 50)),
    'wall': pygame.transform.scale(load_image('wall.png'), (50, 50)),
    'cup': pygame.transform.scale(load_image('cup.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('goose.png'), (50, 50))


# метод завершения программы
def terminate():
    pygame.quit()
    sys.exit()


# метод выхода на главный экран
def back():
    global player, enemy, enemies
    for obj in gc.get_objects():
        if isinstance(obj, Tile):
            obj.kill()
    if not (enemies is None):
        for enem in enemies:
            enem.kill()
    if not (enemy is None):
        enemy.kill()
    if not (player is None):
        player.kill()
    objects.clear()
    pygame.mixer.music.load('music/start_window.mp3')
    pygame.mixer.music.play(-1)
    start_screen()


# стартовый (главный) экран
def start_screen():
    global coin
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('supergoose.png'), (width, height))
    screen.blit(fon, (0, 0))
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# класс кнопок
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


# создаём окно для выбора уровня
def levels():
    global coin
    objects.clear()
    width = 506
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('sgoose.png'), (width, height))
    screen.blit(fon, (0, 0))
    rules = ["          Уровни", "", "Выберите уровень:"]
    font = pygame.font.SysFont('Times New Roman', 60)
    text_coord = 20
    Button(15, 280, 155, 75, 'Уровень 1', labyrinth_level_1)
    Button(175, 280, 155, 75, 'Уровень 2', labyrinth_level_2)
    Button(335, 280, 155, 75, 'Уровень 3', labyrinth_level_3)
    Button(15, 365, 155, 75, 'Уровень 4', labyrinth_level_4)
    Button(175, 365, 155, 75, 'Уровень 5', fly_level)
    Button(335, 365, 155, 75, 'Уровень 6', fly_level_enemies)
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём первый уровень лабиринт с врагом
def labyrinth_level_1():
    global count, coin, player, enemy
    objects.clear()
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    player, enemies, level_x, level_y = generate_level(load_level('labyrinth_level_1.txt'))
    size = width, height = level_x * STEP + STEP, level_y * STEP + STEP
    enemy = enemies[0]
    screen = pygame.display.set_mode(size)
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 500)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (width // 2, height // 2))
            screen.blit(fon, (width // 4, height // 4))
            Button(width // 2 - 175, height - height // 3, 350, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
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
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == ENEMY_EVENT_TYPE:
                    move_enemy(enemy, player, load_level('labyrinth_level_1.txt'))
            if player.rect.x == 500 and player.rect.y == 50:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                if levels_passed[0] == 0:
                    count += 1
                    levels_passed[0] = 1
                    coin += 50
                win_game()
                return
            if player.rect == enemy.rect:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                lose_game()
                return
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём второй уровень лабиринт с врагом
def labyrinth_level_2():
    global count, coin, player, enemy
    objects.clear()
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    player, enemies, level_x, level_y = generate_level(load_level('labyrinth_level_2.txt'))
    size = width, height = level_x * STEP + STEP, level_y * STEP + STEP
    enemy = enemies[0]
    screen = pygame.display.set_mode(size)
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 400)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (width // 2, height // 2))
            screen.blit(fon, (width // 4, height // 4))
            Button(width // 2 - 175, height - height // 3, 350, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
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
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == ENEMY_EVENT_TYPE:
                    move_enemy(enemy, player, load_level('labyrinth_level_2.txt'))
            if player.rect.x == 1250 and player.rect.y == 750:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                if levels_passed[1] == 0:
                    count += 1
                    levels_passed[1] = 1
                    coin += 50
                win_game()
                return
            if player.rect == enemy.rect:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                lose_game()
                return
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём третий уровень лабиринт с врагом
def labyrinth_level_3():
    global count, coin, player, enemy
    objects.clear()
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    player, enemies, level_x, level_y = generate_level(load_level('labyrinth_level_3.txt'))
    size = width, height = level_x * STEP + STEP, level_y * STEP + STEP
    enemy = enemies[0]
    screen = pygame.display.set_mode(size)
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 350)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (width // 2, height // 2))
            screen.blit(fon, (width // 4, height // 4))
            Button(width // 2 - 175, height - height // 3, 350, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
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
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == ENEMY_EVENT_TYPE:
                    move_enemy(enemy, player, load_level('labyrinth_level_3.txt'))
            if player.rect.x == 1050 and player.rect.y == 950:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                if levels_passed[2] == 0:
                    count += 1
                    levels_passed[2] = 1
                    coin += 50
                win_game()
                return
            if player.rect == enemy.rect:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                lose_game()
                return
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём четвертый уровень лабиринт с врагом
def labyrinth_level_4():
    global count, coin, player, enemy
    objects.clear()
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    player, enemies, level_x, level_y = generate_level(load_level('labyrinth_level_4.txt'))
    size = width, height = level_x * STEP + STEP, level_y * STEP + STEP
    enemy = enemies[0]
    screen = pygame.display.set_mode(size)
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 300)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (width // 2, height // 2))
            screen.blit(fon, (width // 4, height // 4))
            Button(width // 2 - 175, height - height // 3, 350, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
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
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == ENEMY_EVENT_TYPE:
                    move_enemy(enemy, player, load_level('labyrinth_level_4.txt'))
            if player.rect.x == 1100 and player.rect.y == 900:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                if levels_passed[3] == 0:
                    count += 1
                    levels_passed[3] = 1
                    coin += 50
                win_game()
                return
            if player.rect == enemy.rect:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                enemy.kill()
                player.kill()
                lose_game()
                return
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём метод для поиска пути для врага
def find_path_step(start, target, level):
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
                    is_free(next_x, next_y, level) and distance[next_y][next_x] == INF:
                distance[next_y][next_x] = distance[y][x] + 1
                prev[next_y][next_x] = (x, y)
                queue.append((next_x, next_y))
    x, y = target
    if distance[y][x] == INF or start == target:
        return start
    while prev[y][x] != start:
        x, y = prev[y][x]
    return x * STEP, y * STEP


# создаём метод перемещения врага
def move_enemy(enemy, player, level):
    past_x, past_y = enemy.rect.x, enemy.rect.y
    next_position = find_path_step((enemy.rect.x // STEP, enemy.rect.y // STEP),
                                   (player.rect.x // STEP, player.rect.y // STEP), level)
    enemy.rect.x, enemy.rect.y = next_position
    if past_x - enemy.rect.x < 0:
        enemy.update_frame('right', 'wolf')
    elif past_x - enemy.rect.x > 0:
        enemy.update_frame('left', 'wolf')
    elif past_y - enemy.rect.y < 0:
        enemy.update_frame('down', 'wolf')
    elif past_y - enemy.rect.y > 0:
        enemy.update_frame('up', 'wolf')


# метод для проверки клеток лабиринта
def is_free(x, y, level):
    if level[y][x] != '#':
        return True
    return False


# создаём уровень с полётом
def fly_level():
    global coin, count, player
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    camera = Camera()
    objects.clear()
    screen = pygame.display.set_mode((500, 350))
    player, enemy, level_x, level_y = generate_level(load_level('fly_level.txt'))
    cam = Player(0, 150, True)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (250, 200))
            screen.blit(fon, (125, 75))
            Button(200, 225, 100, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.rect.x -= STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            lose_game()
                    if event.key == pygame.K_RIGHT:
                        player.rect.x += STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            lose_game()
                    if event.key == pygame.K_DOWN:
                        player.rect.y += STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            lose_game()
                    if event.key == pygame.K_UP:
                        player.rect.y -= STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            lose_game()
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                            coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if not (cam.rect.x - 250 <= player.rect.x <= cam.rect.x + 250):
                    player.kill()
                    lose_game()
            if pygame.sprite.spritecollideany(player, box_group):
                player.kill()
                lose_game()
            if player.rect.x == 3250 and player.rect.y >= 150:
                player.kill()
                if levels_passed[4] == 0:
                    count += 1
                    levels_passed[4] = 1
                    coin += 50
                win_game()
                return
            player.rect.x += 2
            cam.rect.x += 2
            camera.update(cam)
            for sprite in all_sprites:
                camera.apply(sprite, level_x, level_y)
            screen.fill((0, 0, 0))
            camera_group.draw(screen)
            tiles_group.draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём уровень с полётом и врагами
def fly_level_enemies():
    global coin, count, player, enemy
    pygame.mixer.music.load('music/levels.mp3')
    pygame.mixer.music.play(-1)
    camera = Camera()
    objects.clear()
    screen = pygame.display.set_mode((500, 350))
    player, enemies, level_x, level_y = generate_level(load_level('fly_level_enemies.txt'))
    cam = Player(0, 150, True)
    pygame.time.set_timer(ENEMY_EVENT_TYPE, 250)
    paused = False
    while True:
        if paused:
            fon = pygame.transform.scale(load_image('pause_goose.png'), (250, 200))
            screen.blit(fon, (125, 75))
            Button(200, 225, 100, 50, 'Назад', back)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
            for object in objects:
                object.process()
            pygame.display.flip()
            clock.tick(FPS)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.rect.x -= STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            [enemy.kill() for enemy in enemies]
                            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                            lose_game()
                    if event.key == pygame.K_RIGHT:
                        player.rect.x += STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            [enemy.kill() for enemy in enemies]
                            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                            lose_game()
                    if event.key == pygame.K_DOWN:
                        player.rect.y += STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            [enemy.kill() for enemy in enemies]
                            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                            lose_game()
                    if event.key == pygame.K_UP:
                        player.rect.y -= STEP
                        if pygame.sprite.spritecollideany(player, box_group):
                            player.kill()
                            [enemy.kill() for enemy in enemies]
                            pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                            lose_game()
                    if event.key == pygame.K_SPACE:
                        m_pause()
                    if event.key == pygame.K_MINUS:
                        m_minus()
                    if event.key == pygame.K_EQUALS:
                        m_plus()
                    if event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == ENEMY_EVENT_TYPE:
                    for enemy in enemies:
                        move_flying_enemy(enemy, pygame.sprite.spritecollideany(enemy, box_group))
                if not (cam.rect.x - 250 <= player.rect.x <= cam.rect.x + 250):
                    player.kill()
                    [enemy.kill() for enemy in enemies]
                    pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                    lose_game()
            if pygame.sprite.spritecollideany(player, box_group):
                player.kill()
                [enemy.kill() for enemy in enemies]
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                lose_game()
            if pygame.sprite.spritecollideany(player, enemy_group):
                player.kill()
                [enemy.kill() for enemy in enemies]
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                lose_game()
            if player.rect.x == 3250 and player.rect.y == 150:
                pygame.time.set_timer(ENEMY_EVENT_TYPE, 0)
                [enemy.kill() for enemy in enemies]
                player.kill()
                if levels_passed[5] == 0:
                    count += 1
                    levels_passed[5] = 1
                    coin += 50
                win_game()
                return
            player.rect.x += 2
            cam.rect.x += 2
            camera.update(cam)
            for sprite in all_sprites:
                camera.apply(sprite, level_x, level_y)
            screen.fill((0, 0, 0))
            camera_group.draw(screen)
            tiles_group.draw(screen)
            enemy_group.draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


# создаём метод перемещения летающего врага
def move_flying_enemy(enemy, coll):
    if enemy.direct_y == -1 and coll is None:
        enemy.rect.y -= 10
        enemy.update_frame('up', 'eagle')
    elif enemy.direct_y == -1 and coll:
        enemy.rect.y += 10
        enemy.update_frame('up', 'eagle')
        enemy.direct_y = 1
    elif enemy.direct_y == 1 and coll is None:
        enemy.rect.y += 10
        enemy.update_frame('up', 'eagle')
    elif enemy.direct_y == 1 and coll:
        enemy.rect.y -= 10
        enemy.update_frame('up', 'eagle')
        enemy.direct_y = -1


# создаём окно проигрыша
def lose_game():
    global coin
    for obj in gc.get_objects():
        if isinstance(obj, Tile):
            obj.kill()
    objects.clear()
    pygame.mixer.music.load('music/game_over.mp3')
    pygame.mixer.music.play()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('goose6.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["", "", " Вы проиграли:(!", ""]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 50
    Button(80, 400, 350, 70, 'Назад', back)
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём окно победы
def win_game():
    global coin
    for obj in gc.get_objects():
        if isinstance(obj, Tile):
            obj.kill()
    objects.clear()
    pygame.mixer.music.load('music/win.mp3')
    pygame.mixer.music.play()
    width = 550
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('goose7.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["", "    Поздравляем!!!", "Вы прошли уровень!", ""]
    font = pygame.font.SysFont('Times New Roman', 60)
    text_coord = 50
    Button(80, 400, 350, 70, 'Назад', back)
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# метод загрузки уровня
def load_level(level_name):
    level_name = 'data/levels/' + level_name
    with open(level_name, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


# создаём класс тайлов
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'wall':
            self.add(box_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# создаём класс главного героя
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, camera=False):
        if camera:
            super().__init__(camera_group, all_sprites)
        else:
            super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# создаём класс врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        super().__init__(enemy_group, all_sprites)
        if type == 'wolf':
            self.enemy_image = AnimatedSprite(load_image('wolf.png'), 3, 4, 0, 0)
        elif type == 'eagle':
            self.enemy_image = AnimatedSprite(load_image('eagle.png'), 4, 4, 0, 0)
        self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.direct_y = -1

    def update_frame(self, direction, type):
        if type == 'wolf':
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
        elif type == 'eagle':
            self.enemy_image.cur_frame = 4 + self.enemy_image.cur_frame % 4 + 1
            self.enemy_image.image = self.enemy_image.frames[self.enemy_image.cur_frame - 1]
            self.image = pygame.transform.scale(self.enemy_image.image, (50, 50))


# создаём класс камеры
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


# метод для загрузки уровня
def generate_level(level):
    new_player, enemies, x, y = None, [], None, None
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
                enemies.append(Enemy(x, y, 'wolf'))
            elif level[y][x] == '^':
                Tile('empty', x, y)
                enemies.append(Enemy(x, y, 'eagle'))
    return new_player, enemies, x, y


# создаём окно с историей о гусе
def SuperGoose():
    global coin
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём окно с помощью
def help():
    global coin
    objects.clear()
    width = 605
    height = 600
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    with open('output/help1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    name = ["", ""]
    font = pygame.font.SysFont('Times New Roman', 60)
    font1 = pygame.font.SysFont('Times New Roman', 30)
    text_coord = 50
    Button(165, 100, 200, 50, 'Справка', surprise)
    Button(10, 10, 100, 50, 'Назад', back)
    Button(410, 10, 185, 50, 'Страница 2', help_page_2)
    for line in name:
        line_rendered = font.render(line, 1, (0, 0, 0))
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём второе окно с помощью
def help_page_2():
    global coin
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём окно прогресса
def progress():
    global count, coin
    objects.clear()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('goose4.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["        Прогресс", ""]
    text = ['Твой прогресс:', f'                 {count} из 6 уровней!']
    if count == 6:
        text.append('Молодец!')
        text.append('Ты прошёл игру!!!')
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# функция паузы
def m_pause():
    global fl_pause, vol
    fl_pause = not fl_pause
    if fl_pause:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()


# функция увеличения громкости
def m_plus():
    global vol
    vol += 0.1
    pygame.mixer.music.set_volume(vol)


# функция уменьшения громкости
def m_minus():
    global vol
    vol -= 0.1
    pygame.mixer.music.set_volume(vol)


# создаём окно настроек
def settings():
    global coin
    objects.clear()
    width = 640
    height = 500
    screen = pygame.display.set_mode((width, height))
    fon = pygame.transform.scale(load_image('goose5.png'), (width, height))
    screen.blit(fon, (0, 0))
    name = ["           Настройки", ""]
    text = ["Звук:", "           - пауза, на клавиатуре Пробел",
            "           - плюс, на клавиатуре Плюс",
            "           - минус, на клавиатуре Минус"]
    font = pygame.font.SysFont('Times New Roman', 63)
    font1 = pygame.font.SysFont('Times New Roman', 40)
    text_coord = 50
    Button(10, 10, 100, 50, 'Назад', back)
    Button(10, 270, 100, 50, 'Пауза', m_pause)
    Button(10, 325, 100, 50, '+', m_plus)
    Button(10, 380, 100, 50, '-', m_minus)
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)

# окно успешно выполненной покупки
def done():
    global coin
    objects.clear()
    width = 450
    height = 200
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    name = ["", "      Куплено!", ""]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 20
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# окно ошибки
def wrong():
    global coin
    objects.clear()
    width = 305
    height = 200
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    name = ["", "Ошибка!!!", ""]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 20
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# окно успешно выбранного скина
def succes():
    global coin
    objects.clear()
    width = 305
    height = 200
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    name = ["", " Успешно!", ""]
    font = pygame.font.SysFont('Times New Roman', 63)
    text_coord = 20
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# 5 окон покупки скина
def pay():
    global not_press, coin
    if coin < 100:
        wrong()
    else:
        coin -= 100
        not_press = True
        done()


def pay1():
    global not_press1, coin
    if coin < 250:
        wrong()
    else:
        coin -= 250
        not_press1 = True
        done()


def pay2():
    global not_press2, coin
    if coin < 300:
        wrong()
    else:
        coin -= 300
        not_press2 = True
        done()


def pay3():
    global not_press3, coin
    if coin < 1000000:
        wrong()
    else:
        coin -= 1000000
        not_press3 = True
        done()


def pay4():
    global not_press4, coin
    if coin < 1000000:
        wrong()
    else:
        coin -= 1000000
        not_press4 = True
        done()


# 5 окон выбора скина
def choose():
    global not_choose, player_image, not_press, not_choose1, not_choose2, not_choose3, not_choose4
    if not_press is False:
        wrong()
    else:
        player_image = pygame.transform.scale(load_image('white-goose.png'), (50, 50))
        not_choose = True
        not_choose1, not_choose2, not_choose3, not_choose4 = False, False, False, False
        succes()


def choose1():
    global not_choose1, player_image, not_press1, not_choose, not_choose2, not_choose3, not_choose4
    if not_press1 is False:
        wrong()
    else:
        player_image = pygame.transform.scale(load_image('sup_goose.png'), (50, 50))
        not_choose1 = True
        not_choose, not_choose2, not_choose3, not_choose4 = False, False, False, False
        succes()


def choose2():
    global not_choose2, player_image, not_press2, not_choose, not_choose1, not_choose3, not_choose4
    if not_press2 is False:
        wrong()
    else:
        player_image = pygame.transform.scale(load_image('snow-goose.png'), (50, 50))
        not_choose2 = True
        not_choose, not_choose1, not_choose3, not_choose4 = False, False, False, False
        succes()


def choose3():
    global not_choose3, player_image, not_press3, not_choose, not_choose1, not_choose2, not_choose4
    if not_press3 is False:
        wrong()
    else:
        player_image = pygame.transform.scale(load_image('xenon-goose.png'), (50, 50))
        not_choose3 = True
        not_choose, not_choose1, not_choose2, not_choose4 = False, False, False, False
        succes()


def choose4():
    global not_choose4, player_image, not_press4, not_choose, not_choose1, not_choose2, not_choose3
    if not_press4 is False:
        wrong()
    else:
        player_image = pygame.transform.scale(load_image('molodec-goose.png'), (50, 50))
        not_choose4 = True
        not_choose, not_choose1, not_choose2, not_choose4 = False, False, False, False
        succes()


# создаём окно магазина
def shop():
    global coin
    objects.clear()
    width = 520
    height = 500
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    pic = pygame.transform.scale(load_image('white-goose.png'), (100, 100))
    screen.blit(pic, (10, 150))
    pic1 = pygame.transform.scale(load_image('sup_goose.png'), (100, 100))
    screen.blit(pic1, (110, 150))
    pic2 = pygame.transform.scale(load_image('snow-goose.png'), (100, 100))
    screen.blit(pic2, (210, 150))
    pic3 = pygame.transform.scale(load_image('xenon-goose.png'), (100, 100))
    screen.blit(pic3, (310, 150))
    pic4 = pygame.transform.scale(load_image('molodec-goose.png'), (100, 100))
    screen.blit(pic4, (410, 150))
    name = ["         Магазин", ""]
    font = pygame.font.SysFont('Times New Roman', 63)
    font1 = pygame.font.SysFont('Times New Roman', 30)
    text = font1.render("White", True, (0, 0, 0))
    screen.blit(text, (25, 250))
    text1 = font1.render("Super", True, (0, 0, 0))
    screen.blit(text1, (125, 250))
    text2 = font1.render("Snow", True, (0, 0, 0))
    screen.blit(text2, (225, 250))
    text3 = font1.render("Xenon", True, (0, 0, 0))
    screen.blit(text3, (320, 250))
    text4 = font1.render("Molodec", True, (0, 0, 0))
    screen.blit(text4, (410, 250))
    price = font1.render("100", True, (0, 0, 0))
    screen.blit(price, (40, 280))
    price1 = font1.render("250", True, (0, 0, 0))
    screen.blit(price1, (140, 280))
    price2 = font1.render("300", True, (0, 0, 0))
    screen.blit(price2, (235, 280))
    price3 = font1.render("1000000", True, (0, 0, 0))
    screen.blit(price3, (305, 280))
    price4 = font1.render("1000000", True, (0, 0, 0))
    screen.blit(price4, (410, 280))
    your_money = font1.render(f"{coin}", True, (0, 0, 0))
    screen.blit(your_money, (width // 2 - your_money.get_width() // 2, 20))
    pic_coin = pygame.transform.scale(load_image('coin.png'), (30, 30))
    screen.blit(pic_coin,
                ((width // 2 - your_money.get_width() // 2) + your_money.get_width(), 20))
    text_coord = 50
    done = font1.render("  Твой", True, (0, 0, 0))
    now = font1.render("Выбран", True, (0, 0, 0))
    Button(10, 10, 100, 50, 'Назад', back)
    if not_press is False:
        Button(10, 310, 105, 50, 'Хочу', pay)
    else:
        screen.blit(done, (10, 310))
    if not_press1 is False:
        Button(110, 310, 105, 50, 'Хочу', pay1)
    else:
        screen.blit(done, (110, 310))
    if not_press2 is False:
        Button(210, 310, 105, 50, 'Хочу', pay2)
    else:
        screen.blit(done, (210, 310))
    if not_press3 is False:
        Button(310, 310, 105, 50, 'Хочу', pay3)
    else:
        screen.blit(done, (310, 310))
    if not_press4 is False:
        Button(410, 310, 105, 50, 'Хочу', pay4)
    else:
        screen.blit(done, (410, 310))
    if not_choose is False:
        Button(10, 360, 105, 50, 'Взять', choose)
    else:
        screen.blit(now, (10, 360))
    if not_choose1 is False:
        Button(110, 360, 105, 50, 'Взять', choose1)
    else:
        screen.blit(now, (110, 360))
    if not_choose2 is False:
        Button(210, 360, 105, 50, 'Взять', choose2)
    else:
        screen.blit(now, (210, 360))
    if not_choose3 is False:
        Button(310, 360, 105, 50, 'Взять', choose3)
    else:
        screen.blit(now, (310, 360))
    if not_choose4 is False:
        Button(410, 360, 105, 50, 'Взять', choose4)
    else:
        screen.blit(now, (410, 360))
    help_me = font1.render("Сначала купите - потом выберите", True, (255, 0, 0))
    screen.blit(help_me, (10, 430))
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                        coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# создаём окно сюрприза
def surprise():
    global coin
    objects.clear()
    width = 500
    height = 500
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 162, 232))
    name = ["       Сюрприз!", ""]
    text = ["Подарок от разработчиков:", "Нажми Ctrl и  у тебя", "появится целый миллион",
            "гукоинов!"]
    font = pygame.font.SysFont('Times New Roman', 63)
    font1 = pygame.font.SysFont('Times New Roman', 40)
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
                    m_pause()
                elif event.key == pygame.K_MINUS:
                    m_minus()
                elif event.key == pygame.K_EQUALS:
                    m_plus()
                elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                    coin += 1000000
        for object in objects:
            object.process()
        pygame.display.flip()
        clock.tick(FPS)


# запуск программы
start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    pygame.display.flip()
    clock.tick(FPS)
