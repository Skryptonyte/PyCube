class Client:
    def __init__(self,playerName,playerID,conn,server):
        self.playerName = playerName
        self.playerID = playerID
        
        self.positionX = 0
        self.positionY = 0
        self.positionZ = 0
        
        self.world = server.worlds["world"]
        self.conn = conn
    
        self.opLevel = 0
    def setPosition(self,x,y,z):
    	self.positionX = x
    	self.positionY = y
    	self.positionZ = z