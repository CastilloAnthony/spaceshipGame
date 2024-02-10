import pygame
from random import randint, uniform
import time
from math import fabs, cos, sin, tan, radians, degrees, sqrt, acos, asin, atan, pi

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
    
def drawRect(surface:pygame.Surface, x:int, y:int, width:int, height:int, color=(255,255,255,255)):
    # Area = l*w
    # Perimeter = 2l+2w
    tempSurface=pygame.Surface((width,height),depth=32,flags=pygame.SRCALPHA)
    x_pos = 0
    while x_pos < x+width:
        y_pos = 0
        while y_pos < y+height:
            tempSurface.set_at((x_pos,y_pos), color)
            y_pos += 1
        x_pos += 1
    surface.blit(tempSurface, (x, y))

def drawCircle(surface:pygame.Surface, x:int, y:int, radius:float, color=(255,255,255,255)):
    # Area = 2(pi)r**2
    # Perimeter (Circumference) = 2(pi)r
    tempSurface=pygame.Surface((radius*2,radius*2),depth=32,flags=pygame.SRCALPHA)
    # pygame.draw.circle(tempSurface, color, (radius, radius), radius)

    # Blit the circle onto the screen
    # screen.blit(tempSurface, (x - radius, y - radius))
    angle = 0
    while angle < 360:
        r = 0
        while r < radius:
            tempSurface.set_at((radius+round(r*cos(radians(angle))), radius+round(r*sin(radians(angle)))), color)
            r += 1
        angle += 1
    surface.blit(tempSurface, (x-radius,y-radius))

def drawTriangle(surface:pygame.Surface, x:int, y:int, sides:tuple, color=(255,255,255,255)):
    # Area = 1/2 b*h
    # Perimeter = a+b+c; Equilateral = a**3; Right = a+b+sqrt(a**2+b**2)
    if len(sides) == 2: # Assume Right Triangle
        tempSurface=pygame.Surface((sides[0],sides[1]),depth=32,flags=pygame.SRCALPHA)
        y_pos = sides[1]
        while y_pos >= 0:
            x_pos = sides[0]*(y_pos/sides[1])
            while x_pos >= 0:
                tempSurface.set_at((x_pos,y_pos), color)
                x_pos -= 1
            y_pos -= 1
        surface.blit(tempSurface, (x,y))
    elif len(sides) == 3:
        if sides[0] == sides[1] == sides[2]: # Assume Equilateral Triangle
            tempSurface=pygame.Surface((sides[0],sides[1]),depth=32,flags=pygame.SRCALPHA)
            base = (sides[0]-1)/2
            height = sqrt(sides[1]**2-base**2)
            y_pos = height
            while y_pos >= 0:
                x_pos = base*(y_pos/(height))
                while x_pos >= 0:
                    tempSurface.set_at((round(base-x_pos),round(y_pos)), color)
                    tempSurface.set_at((round(x_pos+base),round(y_pos)), color)
                    x_pos -= 1
                y_pos -= 1
            surface.blit(tempSurface, (x,y))
        else: # Non-Equilateral Triangle
            sortedSides = sorted(sides, reverse=True) # [10, 7, 5] etc...
            # print(1, sortedSides[0], sortedSides[1], sortedSides[2]) # a, b, c
            a, b, c = sortedSides[0], sortedSides[1], sortedSides[2]
            A_angle = acos((b**2+c**2-a**2)/(2*b*c))
            B_angle = asin(b*sin(A_angle)/a)
            C_angle = asin(c*sin(A_angle)/a)
            # print('Sides: ', a, b, c)
            # print('Angles: ', degrees(A_angle), degrees(B_angle), degrees(C_angle))
            # print('Total Angle: ', A_angle+B_angle+C_angle, pi)
            height = round(b*sin(C_angle))
            base = round(b*cos(C_angle))#sqrt(b**2-height**2)#b*sin(pi/2-C_angle)
            # print(C_angle+pi/2+pi/2-C_angle,, pi)
            # print(height, base)
            tempSurface=pygame.Surface((a,height),depth=32,flags=pygame.SRCALPHA)
            y_pos = height
            while y_pos > 0:
                x_pos = base*(y_pos/(height))#round(((largest[0]-1))*(y_pos/(largest[1]-1)))
                while x_pos > 0:
                    tempSurface.set_at((int(base-x_pos),int(y_pos)), color)
                    x_pos -= 1
                y_pos -= 1
            base2 = a-base#(90-degrees(acos(sortedSides[2]/sortedSides[0])))
            y_pos = height
            while y_pos > 0:
                x_pos = base2*(y_pos/height)#round(((largest[0]-1))*(y_pos/(largest[1]-1)))
                while x_pos > 0:
                    tempSurface.set_at((int(base+x_pos),int(y_pos)), color)
                    x_pos -= 1
                y_pos -= 1
            surface.blit(tempSurface, (x,y))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color(255,255,255,255))
    screen.fill(pygame.Color(0,0,255, randint(0,255)))
    # screen.blit(newSurface, dest=(0,0))
    if debug:
        fps = pygame.font.SysFont("Times New Roman", round(12)).render('fps: '+str(round(clock.get_fps())), True, (255, 255, 0))
        screen.blit(fps, (0, 0))
        timing = pygame.font.SysFont("Times New Roman", round(12)).render('time: '+str(round(time.time()))+' '+str(round(pygame.time.get_ticks()/1000)), True, (255, 255, 0))
        screen.blit(timing, (0, fps.get_height()))

    #pygame.draw.rect(surface=screen, color=pygame.Color(255, 255, 0,a=randint(0,100)),rect=pygame.Rect(50,50,100,100))#uniform(50,100),uniform(50,100)))
    drawRect(surface=screen, x=400, y= 250, width=100, height=100, color=(255, 255, 0, 150))
    drawCircle(surface=screen, x=400, y= 300, radius=50, color=(255, 255, 0, 150))
    drawTriangle(surface=screen, x=200, y= 150, sides=(400,300,200,), color=(255, 255, 0, 150))

    # Update the display
    pygame.display.update()

    pygame.display.flip()
    clock.tick()