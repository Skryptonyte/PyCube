import queue

class Client:
    def __init__(self,playerName,playerID,conn,server):

        self._extensionsLeft = -1


        self.playerName = playerName
        self.playerID = playerID
        self.CPE = {}
        
        self.positionX = 0
        self.positionY = 0
        self.positionZ = 0
        
        self.messageQueue = queue.Queue()

        self.world = server.worlds["world"]
        self.conn = conn
    
        self.opLevel = 0
    def setPosition(self,x,y,z):
        self.positionX = x
        self.positionY = y
        self.positionZ = z

