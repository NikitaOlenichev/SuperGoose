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
        line_rendered = font.render(line, 1, (random.randint(0, 255), random.randint(0, 255), 0))
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
    print('Уровни скоро появятся!')


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
