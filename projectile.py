from math import cos, sin, fabs, radians

class Projectile():
    def __init__(self, stats:dict=None, pos:dict=None, maxDims:dict=None):
        self.__stats = {
            'Name':'Photon',
            'Owner':None,
            'Speed':100,
            'Damage Type': 'Energy',
            'Damage':10,
        }
        self.__pos = {
            'x':0,
            'y':0,
            'dir':0,
        }
        self.__maxDims = {
            'x':800,
            'y':600,
        }
        if stats != None:
            self.__stats.update(stats)
        if pos != None:
            self.__pos.update(pos)
        if maxDims != None:
            self.__maxDims.update(maxDims)

    def __del__(self):
        del self.__stats, self.__pos, self.__maxDims

    def getStats(self):
        return self.__stats
    
    def getPos(self):
        return self.__pos
    
    def tick(self, timedelta:float=None,):
        self.__pos['x'] += self.__stats['Speed']*cos(radians(self.__pos['dir']))*timedelta
        self.__pos['y'] += self.__stats['Speed']*sin(radians(self.__pos['dir']))*timedelta
        if self.__pos['x'] > self.__maxDims['x'] or self.__pos['x'] < 0 or self.__pos['y'] > self.__maxDims['y'] or self.__pos['y'] < 0:
            del self