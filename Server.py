
from MCClassicLevel import *
from Client import Client
import os
class Server:
    def __init__(self, SERVER_NAME, SERVER_MOTD):
        self.SERVER_NAME = SERVER_NAME
        self.SERVER_MOTD = SERVER_MOTD
        
        self.playerData = {}
        self.playerNameData = {}
        self.connList = [None]*128
        self.worlds = {}
        if (not os.path.exists("maps/world.lvl")):
            generateFlatWorld("maps/world.lvl",128,64,128)
            #world = MCClassicLevel("maps/main.lvl")
        
        for f in os.listdir("maps/"):
            if f.endswith(".lvl"):
                worldName = f[:-4]
                print("Loading map:",worldName)
                self.worlds[worldName] = MCClassicLevel("maps/"+f)
            

        
        #self.worlds["main"] = MCClassicLevel("maps/main.lvl")
    
    def addPlayerID(self,playerName,playerID,conn):
        #playerID = findMinAvailableID()        
        newClient = Client(playerName, playerID,conn,self)
        self.playerData[playerID] = newClient
        self.playerNameData[playerName] = newClient

    def removePlayer(self, playerID):
        if (playerID not in self.playerData.keys()):
            return
        playerName = self.playerData[playerID].playerName
        self.connList[playerID] = None
        
        # Rectify race condition in case player reconnects before looping ping terminates old connection
        if (self.playerData[playerID] == self.playerNameData[playerName]):
            print("Erasing name off entry")
            self.playerNameData.pop(playerName, None)        
        self.playerData.pop(playerID,None)
        
        
