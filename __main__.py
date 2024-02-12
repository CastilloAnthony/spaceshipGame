import pygame
import time
from ship import Ship
from projectile import Projectile
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
        self.__infoPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)#, flags=pygame.SRCALPHA
        self.__targetPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__statusBar = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__stars = pygame.Surface((self.__res_x*4, self.__res_y*4), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__playingField = pygame.Surface((self.__res_x*4, self.__res_y*4), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        self.__uiUpdateSpeed = 0.01
        self.__threads = []
        self.__shipTicks = {}
        self.__screen = None
        pos = {
            'x':self.__playingField.get_width()/2,
            'y':self.__playingField.get_height()/2,
            'x_dir':0,
        }
        maxDims = {
            'x':self.__playingField.get_width(),
            'y':self.__playingField.get_height(),
        }
        self.__player = Ship(name='The Kestral', pos=pos, maxDims=maxDims)
        self.__ships = {'Player':self.__player}
        self.__projectiles = []

    def __del__(self):
        pass

    def start(self):
        pygame.init()
        pygame.display.set_caption('Space Game') # Set the window title
        self.__screen = pygame.display.set_mode((self.__res_x, self.__res_y), depth=self.__colorDepth, flags=pygame.SRCALPHA) #flags=pygame.RESIZABLE, 
        # infoPanel = pygame.Surface((self.__res_x*(3/20), self.__res_y*(2/10)))
        clock = pygame.time.Clock()
        previousTime = pygame.time.get_ticks()/1000
        dt = 0

        # Adding  Ships to the World
        while len(self.__ships) < 10:
            self._generateShip()
        validTargets = []
        for i in self.__ships:
            if i != 'Player':
                validTargets.append(i)
        self.__player.setValidTargets(validTargets)

        # Creating Threads
        # self.__threads.append(Thread(target=self._drawPlayingField, name='_drawPlayingField'))
        # self.__threads[-1].start()
        self.__threads.append(Thread(target=self._generateUI, name='_generateUI'))
        self.__threads[-1].start()
        # self.__threads.append(Thread(target=self._statusBars, name='_statusBars'))
        # self.__threads[-1].start()
        # self.__threads.append(Thread(target=self._generateInfoPanel, name='_generateInfoPanel'))
        # self.__threads[-1].start()
        # self.__threads.append(Thread(target=self._generateTargetPanel, name='_generateTargetPanel'))
        # self.__threads[-1].start()
        self.__threads.append(Thread(target=self._generateStars, name='_generateStars'))
        self.__threads[-1].start()
        
        while self.__running:
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
            # if keys[pygame.K_LSHIFT]:
            #     inputsKeys.append('LSHIFT')
            # if keys[pygame.K_LCTRL]:
            #     inputsKeys.append('LCTRL')
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
            if keys[pygame.K_SPACE]:
                if self.__player.getStats()['Firing Cooldown'] <= 0:
                    self._spawnProjectile(owner='Player')
                    self.__player.fireWeapon()
            # if keys[pygame.K_q]:
            #     inputsKeys.append('q')
            # if keys[pygame.K_e]:
            #     inputsKeys.append('e')

            # Screen Drawing
            self.__screen.fill(pygame.Color(0, 0, 0, 255))
            self.__screen.blit(self.__stars, dest=(0,0), area=(self.__player.getPos()['x']-self.__res_x/2, self.__player.getPos()['y']-self.__res_y/2, self.__res_x, self.__res_y))#,special_flags=pygame.BLEND_ALPHA_SDL2)
            if self.__debug:
                fps = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('fps: '+str(round(clock.get_fps())), True, (255, 255, 0))
                self.__screen.blit(fps, (0, 0))
                timing = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('elapsed time: '+str(round(pygame.time.get_ticks()/1000)), True, (255, 255, 0))
                self.__screen.blit(timing, (0, fps.get_height()))
            self._drawPlayingField()
            self.__screen.blit(self.__playingField, dest=(0,0), area=(self.__player.getPos()['x']-self.__res_x/2, self.__player.getPos()['y']-self.__res_y/2, self.__res_x, self.__res_y))

            # Drawing UI elements
            self.__screen.blit(self.__statusBar, (self.__res_x/2-self.__statusBar.get_width()/2, 10))
            self.__screen.blit(self.__infoPanel, (0, self.__res_y-self.__infoPanel.get_height()))
            self.__screen.blit(self.__targetPanel, (self.__res_x-self.__targetPanel.get_width(), self.__res_y-self.__targetPanel.get_height()))

            # Ticking Ships & Projectiles
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
            for i in self.__projectiles:
                i.tick(timedelta=dt)

            # Update Screen
            pygame.display.flip()
            dt = clock.tick(60)/1000#60)
            self.__uiUpdateSpeed = dt
        pygame.quit()
        
    def _generateUI(self):
        while self.__running:
            # startTime = time.time()
            # Status Bars
            width = self.__res_x/2
            height = self.__res_y/20
            statusBars = pygame.Surface((width, height), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            statusBars.fill(pygame.Color(0,150,150,100))
            # self._drawRect(surface=statusBars, x=0, y=0, width=width, height=height, color=(0,150,150,100))
            pygame.draw.rect(surface=statusBars, color=pygame.Color(0,255,0,200), rect=pygame.Rect(width/50,height-height/10*8,(width-width/50*2)*self.__player.getStats()['Hull']/self.__player.getStats()['Max Hull'],height/4))
            pygame.draw.rect(surface=statusBars, color=pygame.Color(0,100,255,200), rect=pygame.Rect(width/50,height-height/10*4,(width-width/50*2)*self.__player.getStats()['Shields']/self.__player.getStats()['Max Shields'],height/4))
            self.__statusBar = statusBars

            # Info Panel
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

            # Target Panel
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
            # print(self.__uiUpdateSpeed, time.time()-startTime, self.__uiUpdateSpeed-(time.time()-startTime))
            # sleepTimer = self.__uiUpdateSpeed-(time.time()-startTime)
            # if sleepTimer > 0:
            #     time.sleep(sleepTimer)
            # else:
            time.sleep(self.__uiUpdateSpeed)

    # def _generateInfoPanel(self):
    #     while self.__running:
    #         statsHeight = 0
    #         maxWidth = 0
    #         info = []
    #         title = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('Info Panel', True, (0, 0, 0))
    #         info.append(title)
    #         # infoPanel.blit(title, (0,0))
    #         statsHeight += title.get_height()
    #         playerStats = self.__player.displayStats()
    #         for i in playerStats:
    #             # stat = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0))
    #             if isinstance(playerStats[i], float):
    #                 info.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(round(playerStats[i],1)), True, (0, 0, 0)))
    #             else:
    #                 info.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0)))
    #             # infoPanel.blit(stat, (0, 0+statsHeight))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #             statsHeight += info[-1].get_height()
    #             if info[-1].get_width() > maxWidth:
    #                 maxWidth = info[-1].get_width()
    #         infoPanel = pygame.Surface((maxWidth, statsHeight), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #         infoPanel.fill(pygame.Color(0, 150, 200, 200))
    #         height = 0
    #         for i, v in enumerate(info):
    #             if i == 0:
    #                 infoPanel.blit(v, (maxWidth/2-v.get_width()/2, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #                 height += v.get_height()
    #             else:
    #                 infoPanel.blit(v, (0, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #                 height += v.get_height()
    #         infoPanelBack = pygame.Surface((maxWidth*1.1, statsHeight*1.1), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #         infoPanelBack.fill(pygame.Color(0,150,150, 100))
    #         infoPanelBack.blit(infoPanel, (maxWidth*1.1/2-infoPanel.get_width()/2,statsHeight*0.05))
    #         self.__infoPanel = infoPanelBack#pygame.transform.scale(infoPanel, (self.__res_factor*3,self.__res_factor*5))
    #         time.sleep(self.__uiUpdateSpeed)
    #         # return infoPanel
    
    # def _generateTargetPanel(self):
    #     while self.__running:
    #         if self.__player.getTarget() in self.__ships:
    #             target = self.__ships[self.__player.getTarget()]
    #             statsHeight = 0
    #             maxWidth = 0
    #             targetInfo = []
    #             title = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render('Target Panel', True, (0, 0, 0))
    #             targetInfo.append(title)
    #             # infoPanel.blit(title, (0,0))
    #             statsHeight += title.get_height()
    #             targetStats = target.displayStats()
    #             for i in targetStats:
    #                 # stat = pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(playerStats[i]), True, (0, 0, 0))
    #                 if isinstance(targetStats[i], float):
    #                     targetInfo.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(round(targetStats[i], 1)), True, (0, 0, 0)))
    #                 else:
    #                     targetInfo.append(pygame.font.SysFont("Times New Roman", round(12*self.__guiScale)).render(i+': '+str(targetStats[i]), True, (0, 0, 0)))
    #                 # infoPanel.blit(stat, (0, 0+statsHeight))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #                 statsHeight += targetInfo[-1].get_height()
    #                 if targetInfo[-1].get_width() > maxWidth:
    #                     maxWidth = targetInfo[-1].get_width()
    #             targetPanel = pygame.Surface((maxWidth, statsHeight), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #             targetPanel.fill(pygame.Color(0, 150, 200, 200))
    #             height = 0
    #             for i, v in enumerate(targetInfo):
    #                 if i == 0:
    #                     targetPanel.blit(v, (maxWidth/2-v.get_width()/2, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #                     height += v.get_height()
    #                 else:
    #                     targetPanel.blit(v, (0, height))#self.__res_y*(2/10)-stat.get_height()-statsHeight))#statsHeight))
    #                     height += v.get_height()
    #             targetPanelBack = pygame.Surface((maxWidth*1.1, statsHeight*1.1), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #             targetPanelBack.fill(pygame.Color(0,150,150, 100))
    #             targetPanelBack.blit(targetPanel, (maxWidth*1.1/2-targetPanel.get_width()/2,statsHeight*0.05))
    #             self.__targetPanel = targetPanelBack
    #         else: 
    #             self.__targetPanel = pygame.Surface((0,0), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #         time.sleep(self.__uiUpdateSpeed)
    #         # return targetPanel

    # def _statusBars(self):
    #     while self.__running:
    #         width = self.__res_x/2
    #         height = self.__res_y/20
    #         statusBars = pygame.Surface((width, height), depth=self.__colorDepth, flags=pygame.SRCALPHA)
    #         statusBars.fill(pygame.Color(0,150,150,100))
    #         # self._drawRect(surface=statusBars, x=0, y=0, width=width, height=height, color=(0,150,150,100))
    #         pygame.draw.rect(surface=statusBars, color=pygame.Color(0,255,0,200), rect=pygame.Rect(width/50,height-height/10*8,(width-width/50*2)*self.__player.getStats()['Hull']/self.__player.getStats()['Max Hull'],height/4))
    #         pygame.draw.rect(surface=statusBars, color=pygame.Color(0,100,255,200), rect=pygame.Rect(width/50,height-height/10*4,(width-width/50*2)*self.__player.getStats()['Shields']/self.__player.getStats()['Max Shields'],height/4))
    #         self.__statusBar = statusBars
    #         time.sleep(self.__uiUpdateSpeed)

    def _generateShip(self):
        shipnames = []
        with open('shipnames.txt', 'r') as file:
            shipnames = [line.rstrip() for line in file]
            # for line in file:
            #     shipnames.append(line)
        name = shipnames[randint(0,len(shipnames)-1)]
        maxStats = [randint(50,100), randint(50,100), randint(50,100), randint(50,100), randint(50,100), uniform(5,10), randint(1,5)]
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
            'x':randint(self.__playingField.get_width()/16,self.__playingField.get_width()-self.__playingField.get_width()/16),
            'y':randint(self.__playingField.get_height()/9,self.__playingField.get_height()-self.__playingField.get_height()/9),
            # 'z':randint(0,360),
            'x_dir':randint(0,360),
            # 'y_dir':randint(0,360),
            # 'z_dir':randint(0,360),
        }
        maxDims = {
            'x':self.__playingField.get_width(),
            'y':self.__playingField.get_height(),
            # 'z':800,
        }
        self.__ships[stats['Name']] = Ship(name=stats['Name'], stats=stats, pos=pos, maxDims=maxDims)

    def _generateStars(self):
        colors = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
        self.__stars.fill(pygame.Color(0, 0, 25, 100))
        x = 0
        while x <= self.__stars.get_width():
            y = 0
            while y <= self.__stars.get_height():
                rng = randint(0,10)
                if rng == 1:
                    color = randint(0,6)
                    size = randint(1,5)
                    halo = randint(1,3)
                    if colors[color] == 'O':
                        pygame.draw.circle(self.__stars, (100, 100, 255,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (100, 100, 255,randint(100,200)), (x, y), size)
                    elif colors[color] == 'B':
                        pygame.draw.circle(self.__stars, (150, 150, 255,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (150, 150, 255,randint(100,200)), (x, y), size)
                    elif colors[color] == 'A':
                        pygame.draw.circle(self.__stars, (200, 200, 255,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (200, 200, 255,randint(100,200)), (x, y), size)
                    elif colors[color] == 'F':
                        pygame.draw.circle(self.__stars, (255, 255, 255,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (255, 255, 255,randint(100,200)), (x, y), size)
                    elif colors[color] == 'G':
                        pygame.draw.circle(self.__stars, (255, 255, 100,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (255, 255, 255,randint(100,200)), (x, y), size)
                    elif colors[color] == 'K':
                        pygame.draw.circle(self.__stars, (255, 165, 0,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (255, 165, 0,randint(100,200)), (x, y), size)
                    elif colors[color] == 'M':
                        pygame.draw.circle(self.__stars, (255, 100, 100,randint(0,100)), (x, y), size+halo)
                        pygame.draw.circle(self.__stars, (255, 100, 100,randint(100,200)), (x, y), size)
                    else:
                        pass
                y += randint(20,50)
            x += randint(10,30)
    
    def _drawPlayingField(self):
        shipSize = 100
        projectileSize = shipSize/10
        self.__playingField.fill(pygame.Color(0, 0, 0, 0))

        # Drawing PlayingField Boundaries
        pygame.draw.rect(
            surface=self.__playingField, 
            color=(255, 255, 255, 255), 
            rect=(
                self.__playingField.get_width()/16,
                self.__playingField.get_height()/9,
                self.__playingField.get_width()-self.__playingField.get_width()*2/16, 
                self.__playingField.get_height()-self.__playingField.get_height()*2/9
                ), 
                width=1
            )
        
        # Drawing Non-player ships
        for i in self.__ships:
            # print(i)
            shipPos = self.__ships[i].getPos()
            shipInfo = self.__ships[i].getStats()
            shipSurface = pygame.Surface((shipSize*3, shipSize*3), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            if i == 'Player': # We want to draw the player after drawing all the other ships
                pass
            else:
                if shipInfo['Shields'] > 0:
                    pygame.draw.ellipse(
                        surface=shipSurface, 
                        color=(100, 100, 200, int(100*shipInfo['Shields']/shipInfo['Max Shields'])), 
                        rect=(
                            0,
                            0,
                            shipSize*3,
                            shipSize*3,
                            )
                    )
                pygame.draw.polygon(
                    surface=shipSurface, 
                    color=(255, 50, 50, 255),
                    points=[
                        (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir'])), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']))), 
                        (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir']+135)), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']+135))), 
                        (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir']+225)), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']+225)))
                    ]
                )
            if i == self.__player.getTarget():
                pygame.draw.circle(surface=self.__playingField, color=(0, 0, 100, 150), radius=shipSize*1.5, width =int(shipSize/10), center=(shipPos['x'],shipPos['y']))
                pygame.draw.circle(surface=self.__playingField, color=(50, 50, 255, 255), radius=shipSize*1.25, width=int(shipSize/20), center=(shipPos['x'],shipPos['y']))
            self.__playingField.blit(shipSurface, (shipPos['x']-shipSize*1.5, shipPos['y']-shipSize*1.5))
            del shipSurface

        # Drawing Player
        shipPos = self.__player.getPos()
        shipInfo = self.__player.getStats()
        shipSurface = pygame.Surface((shipSize*3, shipSize*3), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        if shipInfo['Shields'] > 0:
            pygame.draw.ellipse(
                        surface=shipSurface, 
                        color=(100, 100, 200, int(100*shipInfo['Shields']/shipInfo['Max Shields'])), 
                        rect=(
                            0,
                            0,
                            shipSize*3,
                            shipSize*3,
                            )
            )
            # shieldSurface = pygame.Surface((shipSize*3, shipSize*2), depth=self.__colorDepth, flags=pygame.SRCALPHA)
            # pygame.draw.ellipse(
            #         surface=shieldSurface, 
            #         color=(100, 100, 200, int(100*shipInfo['Shields']/shipInfo['Max Shields'])), 
            #         rect=(
            #             0,#*cos(radians(-shipPos['x_dir'])),
            #             0,
            #             shipSize*3,
            #             shipSize*2,
            #             )
            # )
            # pygame.transform.rotate(surface=shieldSurface, angle=shipPos['x_dir'])
            # shipSurface.blit(pygame.transform.rotate(surface=shieldSurface, angle=shipPos['x_dir']), (shipSize+shipSize*sin(radians(-shipPos['x_dir'])),shipSize*cos(radians(-shipPos['x_dir']))))
            # del shieldSurface
            # pygame.draw.polygon(surface=shipSurface, color=(100, 100, 200, int(100*shipInfo['Shields']/shipInfo['Max Shields'])),
            #                 points=[
            #                     (shipSize*1.5+(shipSize*1.5)*cos(radians(shipPos['x_dir'])), shipSize*1.5+(shipSize*1.5)*sin(radians(shipPos['x_dir']))), 
            #                     (shipSize*1.5+(shipSize*1.5)*cos(radians(shipPos['x_dir']+135)), shipSize*1.5+(shipSize*1.5)*sin(radians(shipPos['x_dir']+135))), 
            #                     (shipSize*1.5+(shipSize*1.5)*cos(radians(shipPos['x_dir']+225)), shipSize*1.5+(shipSize*1.5)*sin(radians(shipPos['x_dir']+225)))
            #                     ]
            # )
        pygame.draw.polygon(surface=shipSurface, color=(50, 50, 255, 255),
                            points=[
                                (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir'])), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']))), 
                                (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir']+135)), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']+135))), 
                                (shipSize*1.5+shipSize*cos(radians(-shipPos['x_dir']+225)), shipSize*1.5+shipSize*sin(radians(-shipPos['x_dir']+225)))
                                ]
        )
        # pygame.draw.polygon(surface=shipSurface, color=(255, 165, 0, 255),
        #                     points=[
        #                         (shipSize*1.5-shipSize*1.1*cos(radians(-shipPos['x_dir'])), shipSize*1.5-shipSize*1.1*sin(radians(-shipPos['x_dir']))),  
        #                         (shipSize*0.5+shipSize*1.0+shipSize*1.1*cos(radians(-shipPos['x_dir']+135)), shipSize*0.5+shipSize*1.0+shipSize*1.1*sin(radians(-shipPos['x_dir']+135))), 
        #                         (shipSize*0.5+shipSize*1.0+shipSize*1.1*cos(radians(-shipPos['x_dir']+225)), shipSize*0.5+shipSize*1.0+shipSize*1.1*sin(radians(-shipPos['x_dir']+225)))
        #                         ]
        # )
        self.__playingField.blit(shipSurface, (shipPos['x']-shipSize*1.5, shipPos['y']-shipSize*1.5))
        del shipSurface

        # Drawing Projectiles
        projectileSurface = pygame.Surface((projectileSize, projectileSize), depth=self.__colorDepth, flags=pygame.SRCALPHA)
        pygame.draw.circle(surface=projectileSurface, color=(255, 0, 0, 200), radius=projectileSize, center=(projectileSize/2, projectileSize/2))
        pygame.draw.circle(surface=projectileSurface, color=(255, 165, 0, 200), radius=projectileSize*.75, center=(projectileSize/2, projectileSize/2))
        pygame.draw.circle(surface=projectileSurface, color=(255, 255, 0, 200), radius=projectileSize*.5, center=(projectileSize/2, projectileSize/2))
        pygame.draw.circle(surface=projectileSurface, color=(255, 255, 255, 200), radius=projectileSize*.25, center=(projectileSize/2, projectileSize/2))
        for i in self.__projectiles:
            pos = i.getPos()
            self.__playingField.blit(projectileSurface, (pos['x'], pos['y']))
    # end _drawPlayingField
        
    def _spawnProjectile(self, owner:str):
        shipSize = 100
        projectileSize = shipSize/10
        if owner in self.__ships:
            shipPos = self.__ships[owner].getPos()
            stats = {
                'Owner':owner,
                'Speed':self.__ships[owner].getStats()['Speed']+100,
            }
            pos = {
                'x':self.__ships[owner].getPos()['x']+shipSize*8/10*cos(radians(-shipPos['x_dir']))-projectileSize/2, 
                'y':self.__ships[owner].getPos()['y']+shipSize*8/10*sin(radians(-shipPos['x_dir']))-projectileSize/2, 
                'dir':-self.__ships[owner].getPos()['x_dir'],
            }
            maxDims = {
                'x':self.__playingField.get_width()-self.__playingField.get_width()/8,
                'y':self.__playingField.get_height()-self.__playingField.get_height()/8,
            }
            self.__projectiles.append(Projectile(stats=stats, pos=pos, maxDims=maxDims))
# end Interface
        
if __name__ == '__main__':
    newInterface = Interface()
    newInterface.start()