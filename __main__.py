import pygame
import time
from ship import Ship
from threading import Thread
from random import randint, uniform
from math import fabs, cos, sin, radians

class Interface():
    def __init__(self):
        self.__debug = True
        self.__guiScale = 1.5 #1.5 #1.5 is 1080p
        self.__res_factor = 80*self.__guiScale
        self.__res_x, self.__res_y = 16*self.__res_factor, 9*self.__res_factor
        self.__colorDepth = 32
        self.__running = True
        self.__player = Ship('The Kestral')
        self.__ships = {'Player':self.__player}
        self.__stars = pygame.Surface((self.__res_x, self.__res_y), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__infoPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)#, flags=pygame.SRCALPHA
        self.__targetPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__statusBar = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__uiUpdateSpeed = 0.1
        self.__threads = []
        self.__shipTicks = {}

    def __del__(self):
        pass

    def start(self):
        pygame.init()
        pygame.display.set_caption('Space Game') # Set the window title
        screen = pygame.display.set_mode((self.__res_x, self.__res_y), depth=self.__colorDepth, flags=pygame.SRCALPHA) #flags=pygame.RESIZABLE, 
        # infoPanel = pygame.Surface((self.__res_x*(3/20), self.__res_y*(2/10)))
        clock = pygame.time.Clock()
        previousTime = pygame.time.get_ticks()/1000
        self.__threads.append(Thread(target=self._generateStars, name='_generateStars'))
        self.__threads[-1].start()
        self.__threads.append(Thread(target=self._generateInfoPanel, name='_generateInfoPanel'))
        self.__threads[-1].start()
        self.__threads.append(Thread(target=self._statusBars, name='_statusBars'))
        self.__threads[-1].start()
        self.__threads.append(Thread(target=self._generateTargetPanel, name='_generateTargetPanel'))
        self.__threads[-1].start()
        dt = 0
        while self.__running:
            moveForwards, moveBackwards = False, False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.__player.cycleTargets()
                # elif event.type == pygame.MOUSEBUTTONUP:
                    # self.__player.cycleTargets()
                    # pass
            # Movement Controls
            keys = pygame.key.get_pressed()
            inputsKeys = []
            if keys[pygame.K_LSHIFT]:
                inputsKeys.append('LSHIFT')
            if keys[pygame.K_LCTRL]:
                inputsKeys.append('LCTRL')
            if keys[pygame.K_x]:
                inputsKeys.append('x')
            if keys[pygame.K_w]:
                inputsKeys.append('w')
            if keys[pygame.K_s]:
                inputsKeys.append('s')
            if keys[pygame.K_a]:
                inputsKeys.append('a')
            if keys[pygame.K_d]:
                inputsKeys.append('d')
            if keys[pygame.K_q]:
                inputsKeys.append('q')
            if keys[pygame.K_e]:
                inputsKeys.append('e')
            screen.fill(pygame.Color(0, 0, 0, 255))
            screen.blit(self.__stars, dest=(0,0))#,special_flags=pygame.BLEND_ALPHA_SDL2)
            if self.__debug:
                fps = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('fps: '+str(round(clock.get_fps())), True, (255, 255, 0))
                screen.blit(fps, (0, 0))
                timing = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('elapsed time: '+str(round(pygame.time.get_ticks()/1000)), True, (255, 255, 0))
                screen.blit(timing, (0, fps.get_height()))
            if len(self.__ships) < 10:
                self._generateShip()
                validTargets = []
                for i in self.__ships:
                    if i != 'Player':
                        validTargets.append(i)
                self.__player.setValidTargets(validTargets)
            else:
                for i in self.__ships:
                    if i == 'Player':
                        self.__ships[i].tick(timedelta=dt, inputs=inputsKeys)
                    else:
                        if self.__ships[i].getStats()['Name'] not in self.__shipTicks:
                            self.__shipTicks[self.__ships[i].getStats()['Name']] = Thread(target=self.__ships[i].tick, name=self.__ships[i].getStats()['Name'], kwargs={'timedelta':dt})
                            self.__shipTicks[self.__ships[i].getStats()['Name']].start()
                        elif self.__shipTicks[self.__ships[i].getStats()['Name']].is_alive():
                            self.__shipTicks[self.__ships[i].getStats()['Name']].join(dt)
                            if self.__shipTicks[self.__ships[i].getStats()['Name']].is_alive():
                                self.__shipTicks[self.__ships[i].getStats()['Name']].terminate()
                            del self.__shipTicks[self.__ships[i].getStats()['Name']]
                            self.__shipTicks[self.__ships[i].getStats()['Name']] = Thread(target=self.__ships[i].tick, name=self.__ships[i].getStats()['Name'], kwargs={'timedelta':dt})
                            self.__shipTicks[self.__ships[i].getStats()['Name']].start()
                        else:
                            del self.__shipTicks[self.__ships[i].getStats()['Name']]
                            self.__shipTicks[self.__ships[i].getStats()['Name']] = Thread(target=self.__ships[i].tick, name=self.__ships[i].getStats()['Name'], kwargs={'timedelta':dt})
                            self.__shipTicks[self.__ships[i].getStats()['Name']].start()
            screen.blit(self.__infoPanel, (0, self.__res_y-self.__infoPanel.get_height()))
            screen.blit(self.__targetPanel, (self.__res_x-self.__targetPanel.get_width(), self.__res_y-self.__targetPanel.get_height()))
            screen.blit(self.__statusBar, (self.__res_x/2-self.__statusBar.get_width()/2, 10))
            pygame.display.flip()
            dt = clock.tick()/1000#60)
        pygame.quit()
        
    def _generateInfoPanel(self):
        while self.__running:
            statsHeight = 0
            maxWidth = 0
            info = []
            title = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('Info Panel', True, (0, 0, 0))
            info.append(title)
            # infoPanel.blit(title, (0,0))
            statsHeight += title.get_height()
            playerStats = self.__player.displayStats()
            for i in playerStats:
                # stat = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0))
                if isinstance(playerStats[i], float):
                    info.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(round(playerStats[i],1)), True, (0, 0, 0)))
                else:
                    info.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0)))
                # infoPanel.blit(stat, (0, 0+statsHeight))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                statsHeight += info[-1].get_height()
                if info[-1].get_width() > maxWidth:
                    maxWidth = info[-1].get_width()
            infoPanel = pygame.Surface((maxWidth, statsHeight), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            infoPanel.fill(pygame.Color(0, 150, 200, 200))
            height = 0
            for i, v in enumerate(info):
                if i == 0:
                    infoPanel.blit(v, (maxWidth/2-v.get_width()/2, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                    height += v.get_height()
                else:
                    infoPanel.blit(v, (0, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                    height += v.get_height()
            infoPanelBack = pygame.Surface((maxWidth*1.1, statsHeight*1.1), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            infoPanelBack.fill(pygame.Color(0,150,150, 100))
            infoPanelBack.blit(infoPanel, (maxWidth*1.1/2-infoPanel.get_width()/2,statsHeight*0.05))
            self.__infoPanel = infoPanelBack#pygame.transform.scale(infoPanel, (self.__res_factor*3,self.__res_factor*5))
            time.sleep(self.__uiUpdateSpeed)
            # return infoPanel
    
    def _generateTargetPanel(self):
        while self.__running:
            if self.__player.getTarget() in self.__ships:
                target = self.__ships[self.__player.getTarget()]
                statsHeight = 0
                maxWidth = 0
                targetInfo = []
                title = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('Target Panel', True, (0, 0, 0))
                targetInfo.append(title)
                # infoPanel.blit(title, (0,0))
                statsHeight += title.get_height()
                targetStats = target.displayStats()
                for i in targetStats:
                    # stat = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0))
                    if isinstance(targetStats[i], float):
                        targetInfo.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(round(targetStats[i], 1)), True, (0, 0, 0)))
                    else:
                        targetInfo.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(targetStats[i]), True, (0, 0, 0)))
                    # infoPanel.blit(stat, (0, 0+statsHeight))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                    statsHeight += targetInfo[-1].get_height()
                    if targetInfo[-1].get_width() > maxWidth:
                        maxWidth = targetInfo[-1].get_width()
                targetPanel = pygame.Surface((maxWidth, statsHeight), depth=self.__colorDepth, flags=pygame.SRCALPHA)
                targetPanel.fill(pygame.Color(0, 150, 200, 200))
                height = 0
                for i, v in enumerate(targetInfo):
                    if i == 0:
                        targetPanel.blit(v, (maxWidth/2-v.get_width()/2, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                        height += v.get_height()
                    else:
                        targetPanel.blit(v, (0, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
                        height += v.get_height()
                targetPanelBack = pygame.Surface((maxWidth*1.1, statsHeight*1.1), depth=self.__colorDepth, flags=pygame.SRCALPHA)
                targetPanelBack.fill(pygame.Color(0,150,150, 100))
                targetPanelBack.blit(targetPanel, (maxWidth*1.1/2-targetPanel.get_width()/2,statsHeight*0.05))
                self.__targetPanel = targetPanelBack
            else: 
                self.__targetPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            time.sleep(self.__uiUpdateSpeed)
            # return targetPanel

    def _statusBars(self):
        while self.__running:
            width = self.__res_x/2
            height = self.__res_y/20
            statusBars = pygame.Surface((width, height), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            statusBars.fill(pygame.Color(0,150,150,100))
            # self._drawRect(surface=statusBars, x=0, y=0, width=width, height=height, color=(0,150,150,100))
            pygame.draw.rect(surface=statusBars, color=pygame.Color(0,255,0,200), rect=pygame.Rect(width/50,height-height/10*8,(width-width/50*2)*self.__player.getStats()['Hull']/self.__player.getStats()['Max Hull'],height/4))
            pygame.draw.rect(surface=statusBars, color=pygame.Color(0,100,255,200), rect=pygame.Rect(width/50,height-height/10*4,(width-width/50*2)*self.__player.getStats()['Shields']/self.__player.getStats()['Max Shields'],height/4))
            self.__statusBar = statusBars
            time.sleep(self.__uiUpdateSpeed)

    def _generateShip(self):
        shipnames = []
        with open('shipnames.txt', 'r') as file:
            shipnames = [line.rstrip() for line in file]
            # for line in file:
            #     shipnames.append(line)
        name = shipnames[randint(0,len(shipnames)-1)]
        maxStats = [randint(50,100), randint(50,100), randint(50,100), randint(50,100), randint(1,10), uniform(0.1,2), randint(1,10)]
        stats = {
            'Name':name, 
            'Type':'Viper', 
            'Class':'Fighter', 
            'Max Hull':maxStats[0],
            'Hull':randint(10,maxStats[0]), 
            'Max Reactor Power':maxStats[1],
            'Reactor Power':randint(50,maxStats[2]), 
            'Max Shields':maxStats[3], 
            'Shields':randint(0,maxStats[3]), 
            'Shield Recharge Rate':uniform(0.1,2),
            'Sheild Recharge Delay':randint(5, 10),
            'Max Speed':maxStats[4], 
            'Speed':0.0,
            'Max Acceleration':maxStats[5],
            'Acceleration Rampup':uniform(0.1,maxStats[5]), 
            'Acceleration':uniform(0.1,maxStats[5]), 
            'Max Cargo':maxStats[6],
            'Cargo':randint(0,maxStats[6]),
            }
        pos = {
            'x':randint(0,360),
            'y':randint(0,360),
            'z':randint(0,360),
            'x_dir':randint(0,360),
            'y_dir':randint(0,360),
            'z_dir':randint(0,360),
        }
        self.__ships[stats['Name']] = Ship(name=stats['Name'], stats=stats, pos=pos)

    def _generateStars(self):
        # self.__stars.fill(pygame.Color(0,0,0,255))
        self.__stars.fill(pygame.Color(0, 0, 25, 100))
        x = 0
        while x <= self.__res_x:
            y = 0
            while y <= self.__res_y:
                rng = randint(0,10)
                if rng == 1:
                    r, radius = 0, randint(5,10)
                    while r < radius:
                        halo_alpha = randint(50,127)
                        star_alpha = halo_alpha*2+1
                        a, angle = 0, 360
                        while a < angle:
                            self.__stars.set_at((x+int(r*cos((radians(a)))),y+int(r*sin((radians(a))))), (255,255,0,halo_alpha))# Yellow
                            self.__stars.set_at((x+int(r/2*cos((radians(a)))),y+int(r/2*sin((radians(a))))), (255,255,255,star_alpha)) # White
                            a += 1
                        r += 0.1
                    # pygame.draw.rect(surface=self.__stars, color=pygame.Color(255, 255, 0,randint(0,150)),rect=pygame.Rect(x,y,uniform(0,10),uniform(0,5)))
                    # pygame.draw.rect(surface=self.__stars, color=pygame.Color(255, 255, 255,randint(50,255)),rect=pygame.Rect(x,y,uniform(0,5),uniform(0,5)))
                y += randint(20,50)
            x += randint(10,30)

    def _drawRect(surface:pygame.Surface, x:int, y:int, width:int, height:int, color):
        tempSurface=pygame.Surface((width,height),depth=32,flags=pygame.SRCALPHA)
        x_pos = x
        while x_pos < x+width:
            y_pos = y
            while y_pos < y+height:
                tempSurface.set_at((x_pos,y_pos), color)
                y_pos += 1
            x_pos += 1
        surface.blit(tempSurface, (x, y))
# end Interface
        
if __name__ == '__main__':
    newInterface = Interface()
    newInterface.start()