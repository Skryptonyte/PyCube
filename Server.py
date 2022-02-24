
from MCClassicLevel import *
from Client import Client
import queue
import os
import protocol

class Server:
    def __init__(self, SERVER_NAME, SERVER_MOTD):
        self.SERVER_NAME = SERVER_NAME
        self.SERVER_MOTD = SERVER_MOTD
        
        self.playerData = {}
        self.playerNameData = {}
        self.connList = [None]*128
        self.allocatedSlots = [0]*128
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
        print("Adding new player ID: ",playerID, "Name:",playerName)
        newClient = Client(playerName, playerID,conn,self)
        self.playerData[playerID] = newClient

    def removePlayer(self, playerID):
        if (playerID not in self.playerData.keys()):
            return
        playerName = self.playerData[playerID].playerName
        self.connList[playerID] = None
        

        # Rectify race condition in case player reconnects before looping ping terminates old connection
        if (playerName != "" and self.playerData[playerID] == self.playerNameData[playerName]):
            print("Erasing name off entry")
            self.playerNameData.pop(playerName, None)        
        self.playerData.pop(playerID,None)

    def sendMessage(self,conn,data):
        self.messageQueue.append(conn,data)

    def workerThread(self,server,playerID):
        print("Beginning worker thread")

        connList = server.connList
        messageQueue = self.playerData[playerID].messageQueue
        while True:
            while ((messageQueue).qsize() > 0):
                #print("Packets to process: "+str(messageQueue.qsize()))
                item = messageQueue.get()
                try:
                    if (self.playerData.get(item[0],None)):
                        self.playerData[item[0]].conn.send(item[1])
                except Exception as e:
                    print("Player disconnected, ID:",playerID)

                    player = server.playerData.get(playerID,None)
                    

                    username = player.playerName

                    protocol.despawnPlayerBroadcast(server, connList,playerID)
                    if (username != ""):
                        protocol.serverMessageBroadcast(server, connList,username + " has left the game.")
                    else:
                        print("Kicking invalid player")
                    server.removePlayer(playerID)          

                    connList[playerID] = None
                    self.allocatedSlots[playerID] = 0
                                                  