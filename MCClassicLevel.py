
import gzip
import threading
import struct
import random

worldlock = threading.Lock()
class MCClassicLevel:
    def __init__(self, fileName):

        world = bytearray(gzip.open(fileName).read())

        self.fileName = fileName
        self.world = world

        magicNumber = struct.unpack('h',world[0:2])[0]
        assert(magicNumber == 1874)

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
        
        checkBounds = (x >= 0 and y >= 0 and z >= 0) and (x < self.worldX and y < self.worldY and z < self.worldZ)

        if (not checkBounds):
            print("Attempt to set block outside allowed limits")
            return
        
        calculatedIndex = 18+x + self.worldX*(z+self.worldZ*y)
        if (mode == 1):
            self.world[calculatedIndex] = block
        elif (mode == 0):
            self.world[calculatedIndex] = 0
                
        
    def saveWorld(self):
        print("[INFO] Saving world!")
        f = gzip.open(self.fileName,"wb")
        f.write(self.world)
        f.close()
        
        
        
        
def generateFlatWorld(fileName,worldX, worldY, worldZ):
    print("Generating new flat world at", fileName)
    volume = worldX*worldY*worldZ
    blocksArray = bytearray(volume)
    
    f = gzip.open(fileName,"wb+")
    
    f.write(struct.pack('h',1874))
    
    f.write(struct.pack('h',worldX))
    f.write(struct.pack('h',worldZ))
    f.write(struct.pack('h',worldY))
    
    
    spawnX = worldX >> 1
    spawnY = (worldY >> 1) + 1
    spawnZ = worldZ >> 1
    f.write(struct.pack('h',spawnX))
    f.write(struct.pack('h',spawnZ))
    f.write(struct.pack('h',spawnY))
    
    f.write(struct.pack('B',0))
    f.write(struct.pack('B',0))
    
    f.write(struct.pack('B',0))
    f.write(struct.pack('B',0))
    
    maxY = worldY >> 1
    
    print("Calculating")
    for y in range(maxY):
        for x in range(worldX):
            for z in range(worldZ):
                
                calculatedIndex = x + worldX*(z+worldZ*y)
                
                if (y == maxY-1):
                    blocksArray[calculatedIndex] = 2
                else:
                    blocksArray[calculatedIndex] = 3
                
                
    print("Writing to file")
    f.write(blocksArray)
        
    f.close()
    print("Finished")
    

# EXPERIMENTAL
"""
import opensimplex
def noise2D(x,z):
    return 0.5*(opensimplex.noise2(x,z) + 1.0)

def generateSimplexWorld(fileName,worldX, worldY, worldZ):
    print("Generating new procedural world at", fileName)
    volume = worldX*worldY*worldZ
    blocksArray = bytearray(volume)
    
    print("Size: ",worldX, worldY, worldZ)
    f = gzip.open(fileName,"wb+")
    
    f.write(struct.pack('h',1874))
    
    f.write(struct.pack('h',worldX))
    f.write(struct.pack('h',worldZ))
    f.write(struct.pack('h',worldY))
    
    
    spawnX = worldX >> 1
    spawnY = (worldY >> 1) + 1
    spawnZ = worldZ >> 1
    
    print(spawnX, spawnY, spawnZ)
    f.write(struct.pack('h',spawnX))
    f.write(struct.pack('h',spawnZ))
    f.write(struct.pack('h',spawnY))
    
    f.write(struct.pack('B',0))
    f.write(struct.pack('B',0))
    
    f.write(struct.pack('B',0))
    f.write(struct.pack('B',0))
    
    maxY = worldY >> 1
    
    print("Calculating")

    opensimplex.seed(random.randint(0,2**64))
    for x in range(worldX):
        for z in range(worldZ):
            
            amp = 0.0
            octaveCount = 20
            currentAmp = 1.0
            freq = 10
            n = 0
            for o in range(octaveCount):
                n += currentAmp*noise2D(freq*x/worldX,freq*z/worldZ)
                amp += currentAmp
                freq *= 2
                currentAmp *= 0.5
            n = n / amp
            #n = n ** 2
            maxY = 50 + int(n*200)
            for y in range(maxY):
                calculatedIndex = x + worldX*(z+worldZ*y)
                
                if (y == maxY-1):
                    if maxY >= ((worldY >> 1)+3):
                        blocksArray[calculatedIndex] = 2
                    elif (abs(maxY-(worldY>>1)) <= 3):
                        blocksArray[calculatedIndex] = 12
                    else:
                        blocksArray[calculatedIndex] = 3
                elif (y <= maxY-5 ):
                    blocksArray[calculatedIndex] = 1
                else:
                    if (abs(maxY-(worldY>>1)) <= 3):
                        blocksArray[calculatedIndex] = 12
                    else:
                        blocksArray[calculatedIndex] = 3
                    
            for y in range(maxY, (worldY >> 1) + 1):
                calculatedIndex = x + worldX*(z+worldZ*y)
                blocksArray[calculatedIndex] = 9
                
                
    

    print("Writing to file")
    f.write(blocksArray)
        
    f.close()
    print("Finished")

"""
if __name__ == "__main__":

    worldName = input("Enter world name: ")
    print("Enter sizes: ")
    x = int(input("Enter x: "))
    y = int(input("Enter y: "))
    z = int(input("Enter z: "))

    generateFlatWorld("maps/"+worldName+".lvl",x,y,z)




