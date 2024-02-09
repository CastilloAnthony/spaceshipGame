import pygame
from random import randint, uniform
import time
from math import cos, sin, radians

pygame.init()
pygame.display.set_caption('Space Game') # Set the window title
screen = pygame.display.set_mode((800, 600),depth=32,flags=pygame.SRCALPHA)#, flags=pygame.BLEND_ALPHA_SDL2)
clock = pygame.time.Clock()
running = True
debug = True
screen.fill(pygame.Color(0,0,255, a=50))

# newSurface = pygame.Surface((800, 600),depth=32,flags=pygame.SRCALPHA)
# x = 0
# while x < 800:
#     y = 0
#     while y < 600:
#         newSurface.set_at((x,y), (200,200,200,randint(0,150)))
#         # print(x,y)
#         y += 1
#     x += 1

# for x in range(0,800):
#     for y in range(0,600):
#         screen.set_at((x,y), (255,255,255,randint(0,150)))
#         print(x,y)
    
def drawRect(surface:pygame.Surface, x:int, y:int, width:int, height:int, color):
    tempSurface=pygame.Surface((width,height),depth=32,flags=pygame.SRCALPHA)
    x_pos = x
    while x_pos < x+width:
        y_pos = y
        while y_pos < y+height:
            tempSurface.set_at((x_pos,y_pos), color)
            y_pos += 1
        x_pos += 1
    surface.blit(tempSurface, (x, y))

def drawCircle(surface:pygame.Surface, x:int, y:int, radius:float, color):
    tempSurface=pygame.Surface((radius*2,radius*2),depth=32,flags=pygame.SRCALPHA)
    angle = 0
    while angle < 360:
        r = 0
        while r < radius:
            tempSurface.set_at((int(radius+r*cos(radians(angle))), int(radius+r*sin(radians(angle)))), color)
            r += 1
        angle += 1
    surface.blit(tempSurface, (x,y))

def drawTriangle():
    # Area = 1/2 b*h
    # Perimeter = b+
    pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color(0,0,255, a=50))
    # screen.blit(newSurface, dest=(0,0))
    if debug:
        fps = pygame.font.SysFont("Times New Roman", round(12)).render('fps: '+str(round(clock.get_fps())), True, (255, 255, 0))
        screen.blit(fps, (0, 0))
        timing = pygame.font.SysFont("Times New Roman", round(12)).render('time: '+str(round(time.time()))+' '+str(round(pygame.time.get_ticks()/1000)), True, (255, 255, 0))
        screen.blit(timing, (0, fps.get_height()))

    #pygame.draw.rect(surface=screen, color=pygame.Color(255, 255, 0,a=randint(0,100)),rect=pygame.Rect(50,50,100,100))#uniform(50,100),uniform(50,100)))
    drawRect(surface=screen, x=50, y= 50, width=100, height=100, color=(255, 255, 0, 150))
    drawCircle(surface=screen, x=200, y= 200, radius=5, color=(255, 255, 0, 255))

    
    pygame.display.flip()
    clock.tick()