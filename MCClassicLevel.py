
import gzip
import threading
import struct

worldlock = threading.Lock()
class MCClassicLevel:
    def __init__(self, fileName):

        world = gzip.open(fileName).read()
        self.fileName = fileName
        self.worldArray = list(world)
        self.world = world
        self.worldX = struct.unpack('h',world[2:4])[0]
        self.worldZ = struct.unpack('h',world[4:6])[0]
        self.worldY = struct.unpack('h',world[6:8])[0]
    
        self.spawnX = struct.unpack('h',world[8:10])[0] << 5
        self.spawnZ = struct.unpack('h',world[10:12])[0] << 5
        self.spawnY = struct.unpack('h',world[12:14])[0] << 5
    
        self.heading = struct.unpack('B',world[14:15])[0]
        self.pitch = struct.unpack('B',world[15:16])[0]
        
    def setBlock(self,x,y,z,mode,block):
        
        print("SET BLOCK:",block,"at (",x,y,z,")")
                
        calculatedIndex = 18+x + self.worldX*(z+self.worldZ*y)
        if (mode == 1):
            self.worldArray[calculatedIndex] = block
        elif (mode == 0):
            self.worldArray[calculatedIndex] = 0
                
        self.world = bytes(self.worldArray)
        
    def saveWorld(self):
        print("[INFO] Saving world!")
        f = gzip.open(self.fileName,"wb")
        f.write(self.world)
        f.close()
        
        
        
        
