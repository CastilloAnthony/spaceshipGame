from math import fabs, cos, radians

class Ship():
    def __init__(self, name:str=None, stats=None, pos=None, maxDims:dict=None):
        self.__stats = {
                'Name':'Unnamed', 
                'Type':'Viper', 
                'Class':'Fighter', 
                'Max Hull':100,
                'Hull':100, 
                'Max Reactor Power':100,
                'Reactor Power':100, 
                'Max Shields':100, 
                'Shields':0, 
                'Shield Recharge Rate':5,
                'Sheild Recharge Delay':5,
                'Rotation Speed':10,
                'Max Speed':100, 
                'Speed':0.0,
                'Max Acceleration':1,
                'Acceleration Rampup':0.1, 
                'Acceleration':0.0, 
                'Max Cargo':10,
                'Cargo':2,
            }
        self.__pos = {
            'x':0,
            'y':0,
            'z':0,
            'x_dir':0,
            'y_dir':0,
            'z_dir':0,
        }
        self.__maxDims = {
            'x':800,
            'y':600,
            'z':800,
        }
        if stats != None:
            self.__stats.update(stats)
        if pos != None:
            self.__pos.update(pos)
        if maxDims != None:
            self.__maxDims.update(maxDims)
        if name != None:
            self.__stats['Name'] = name
        
        self.__target = None
        self.__currentTarget = 0
        self.__validTargets = []
        self.__shield_recharge_delay = self.__stats['Sheild Recharge Delay']

    def __del__(self):
        del self.__stats

    def getPos(self):
        return self.__pos
    
    def getStats(self):
        return self.__stats
    
    def displayStats(self):
        stats = {
            'Name':self.__stats['Name'],
            'Type':self.__stats['Type'],
            'Class':self.__stats['Class'],
            'Hull':self.__stats['Hull'],
            'Reactor Power':self.__stats['Reactor Power'],
            'Shields':self.__stats['Shields'],
            'Speed':self.__stats['Speed'],
            'Acceleration':self.__stats['Acceleration'],
            'Cargo':self.__stats['Cargo'],
        }
        stats.update(self.__pos)
        return stats

    def setName(self, name:str):
        self.__stats['Name'] = name

    def setTarget(self, target:str):
        self.__target = target

    def getTarget(self):
        return self.__target

    def takeDmg(self, damage:float):
        if self.__stats['Shields'] > 0+damage:
            self.__stats['Hull'] -= damage-self.__stats['Shields']
            self.__stats['Shields'] = 0
        else:
            self.__stats['Hull'] -= damage
        self.__shield_recharge_delay = self.__stats['Sheild Recharge Delay']
        
    def cycleTargets(self):
        if self.__currentTarget == None:
            self.__currentTarget = 0
            self.__target = self.__validTargets[self.__currentTarget]
        elif self.__currentTarget < len(self.__validTargets)-1:
            self.__currentTarget += 1
            self.__target = self.__validTargets[self.__currentTarget]
        else:
            self.__currentTarget = None
            self.__target = None

    def setValidTargets(self, validTargets:list):
        self.__validTargets = validTargets

    def tick(self, timedelta:float=None, inputs:list=None):
        # Key Inputs
        if inputs != None:
            for i in inputs:
                # print(i)
                if i == 'LSHIFT': # Accelerate Forwards
                    if self.__stats['Acceleration']+self.__stats['Acceleration Rampup']*timedelta <= self.__stats['Max Acceleration']:
                        self.__stats['Acceleration'] += self.__stats['Acceleration Rampup']*timedelta
                elif i == 'LCTRL': # Accelerate Backwards
                    if self.__stats['Acceleration']-self.__stats['Acceleration Rampup']*timedelta >= -self.__stats['Max Acceleration']:
                        self.__stats['Acceleration'] -= self.__stats['Acceleration Rampup']*timedelta
                elif i == 'x': # Stop Acceleration & Possibly Speed
                    if fabs(self.__stats['Acceleration']) <= 0.1:
                        self.__stats['Acceleration'] = 0.0
                        if fabs(self.__stats['Speed']) <= 0.1:
                            self.__stats['Speed'] = 0.0
                    elif self.__stats['Acceleration'] > 0.0:
                        self.__stats['Acceleration'] -= self.__stats['Acceleration Rampup']*timedelta
                    elif self.__stats['Acceleration'] < 0.0:
                        self.__stats['Acceleration'] += self.__stats['Acceleration Rampup']*timedelta
                elif i == 's': # Pitch Upwards
                    if self.__pos['y_dir']+self.__stats['Rotation Speed']*timedelta <= 360:
                        self.__pos['y_dir'] += self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['y_dir'] += self.__stats['Rotation Speed']*timedelta-360
                elif i == 'w': # Pitch Downwards
                    if self.__pos['y_dir']-self.__stats['Rotation Speed']*timedelta >= 0:
                        self.__pos['y_dir'] -= self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['y_dir'] += 360-self.__stats['Rotation Speed']*timedelta
                elif i == 'a': # Yaw Left
                    if self.__pos['x_dir']+self.__stats['Rotation Speed']*timedelta <= 360:
                        self.__pos['x_dir'] += self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['x_dir'] += self.__stats['Rotation Speed']*timedelta-360
                elif i == 'd': # Yaw Right
                    if self.__pos['x_dir']-self.__stats['Rotation Speed']*timedelta >= 0:
                        self.__pos['x_dir'] -= self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['x_dir'] += 360-self.__stats['Rotation Speed']*timedelta
                elif i == 'q': # Roll Counter-Clockwise
                    if self.__pos['z_dir']+self.__stats['Rotation Speed']*timedelta <= 360:
                        self.__pos['z_dir'] += self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['z_dir'] += self.__stats['Rotation Speed']*timedelta-360
                elif i == 'e': # Roll Clockwise
                    if self.__pos['z_dir']-self.__stats['Rotation Speed']*timedelta >= 0:
                        self.__pos['z_dir'] -= self.__stats['Rotation Speed']*timedelta
                    else:
                        self.__pos['z_dir'] += 360-self.__stats['Rotation Speed']*timedelta

        # Shield Info
        if self.__shield_recharge_delay <= 0:
            if self.__stats['Shields']+self.__stats['Shield Recharge Rate']*timedelta >= self.__stats['Max Shields']:
                self.__stats['Shields'] = self.__stats['Max Shields']
            elif self.__stats['Shields']+self.__stats['Shield Recharge Rate']*timedelta < self.__stats['Max Shields']:
                self.__stats['Shields'] += self.__stats['Shield Recharge Rate']*timedelta
        else:
            self.__shield_recharge_delay -= 1*timedelta

        # Acceleration Affecting Speed
        if fabs(self.__stats['Speed']+self.__stats['Acceleration']) >= self.__stats['Max Speed']:
            if self.__stats['Acceleration'] > 0:
                self.__stats['Speed'] = self.__stats['Max Speed']
            else:
                self.__stats['Speed'] = -self.__stats['Max Speed']
        elif fabs(self.__stats['Speed']+self.__stats['Acceleration']*timedelta) < self.__stats['Max Speed']:
            self.__stats['Speed'] += self.__stats['Acceleration']*timedelta

        # Speed
        if fabs(self.__stats['Speed']) > 0.0:
            self.__pos['x'] += self.__stats['Speed']*cos(radians(self.__pos['x_dir']))*timedelta
            if self.__pos['x'] > self.__maxDims['x']:
                self.__pos['x'] = self.__pos['x']-self.__maxDims['x']
                # self.__pos['y'] = self.__pos['y']-self.__maxDims['y']
                # self.__pos['z'] = self.__pos['z']-self.__maxDims['z']
            elif self.__pos['x'] < 0:
                self.__pos['x'] = self.__pos['x']+self.__maxDims['x']
                # self.__pos['y'] = self.__pos['y']+self.__maxDims['y']
                # self.__pos['z'] = self.__pos['z']+self.__maxDims['z']
            self.__pos['y'] += self.__stats['Speed']*cos(radians(self.__pos['y_dir']))*timedelta
            if self.__pos['y'] > self.__maxDims['y']:
                # self.__pos['x'] = self.__pos['x']-self.__maxDims['x']
                self.__pos['y'] = self.__pos['y']-self.__maxDims['y']
                # self.__pos['z'] = self.__pos['z']-self.__maxDims['z']
            if self.__pos['y'] < 0:
                # self.__pos['x'] = self.__pos['x']+self.__maxDims['x']
                self.__pos['y'] = self.__pos['y']+self.__maxDims['y']
                # self.__pos['z'] = self.__pos['z']+self.__maxDims['z']
            self.__pos['z'] += self.__stats['Speed']*cos(radians(self.__pos['z_dir']))*timedelta
            if self.__pos['z'] > self.__maxDims['z']:
                # self.__pos['x'] = self.__pos['x']-self.__maxDims['x']
                # self.__pos['y'] = self.__pos['y']-self.__maxDims['y']
                self.__pos['z'] = self.__pos['z']-self.__maxDims['z']
            elif self.__pos['z'] < 0:
                # self.__pos['x'] = self.__pos['x']+self.__maxDims['x']
                # self.__pos['y'] = self.__pos['y']+self.__maxDims['y']
                self.__pos['z'] = self.__pos['z']+self.__maxDims['z']
        # elif self.__stats['Speed']+self.__stats['Acceleration'] > self.__stats['Max Speed']:
# end Ship