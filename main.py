import socket
import threading
import protocol
import time
import gzip

from MCClassicLevel import MCClassicLevel
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('127.0.0.1', 25565))
s.listen()


world = MCClassicLevel("maps/main.lvl")
connList = [None]*128


def findMinAvailableID():
    for i in range(128):
        if (connList[i] == None):
            return i
            
    return -1
def processClient(playerID,conn,addr):
    """
    while True:

        data = conn.recv(1024)
        if (data):
            packetID = int(data[0])
            print("Address: ", addr,"Packet ID: ",packetID,len(data))
            
            connList[playerID] = conn
            
            if (packetID in protocol.clientPacketDict.keys()):
                protocol.clientPacketDict[packetID](connList,playerID,data,conn,world)
    """
    buffer = b''
    packetID = None
    
    while True:

        data = conn.recv(1024)
        if (data):
            buffer += data
            
        packetID = int(buffer[0])
        
        while (len(buffer) > 0 and protocol.clientPacketLengths[packetID] <= len(buffer)):
            #print("Address: ", addr,"Packet ID: ",packetID,len(data))
            
            connList[playerID] = conn
            expectedLength = protocol.clientPacketLengths[packetID]
            
            packetData = buffer[0:expectedLength]
            
            buffer = buffer[expectedLength:]
            if (packetID in protocol.clientPacketDict.keys()):
                protocol.clientPacketDict[packetID](connList,playerID,packetData,conn,world)
                
            if (len(buffer) > 0):
                packetID = int(buffer[0])

    print("End of thread")


def pingEveryone(connList):
    while True:
        #print("PING BROADCAST")
        for p in range(128):
            if (connList[p] != None):
                try:
                    protocol.ping(connList[p])
                except:
                    print("Player disconnected, ID:",p)
                    connList[p] = None
                    protocol.despawnPlayerBroadcast(connList,p)
                    protocol.serverMessageBroadcast(connList,protocol.playerIDToName[p] + " has left the game.")
                    
                    protocol.playerNameToID.pop(protocol.playerIDToName[p],None)
                    protocol.playerIDToName.pop(p,None)
                    
                    
                    
        time.sleep(1)
if __name__ == "__main__":
    playerCount = 0
    
    pingThread = threading.Thread(target=pingEveryone, args=(connList,))
    pingThread.start()

    while True:
        conn, addr = s.accept()
        
        playerID = findMinAvailableID()
        if (playerID < 0):
            continue
        
        t1 = threading.Thread(target=processClient,args=(playerID,conn,addr))
        print("New connection from address:",addr);
        t1.start()
        
        
    s.close()



