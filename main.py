import socket
import threading
import protocol
import time
import gzip
import os

import heartbeat

from MCClassicLevel import *
from Server import Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Disable Nagle Algorithm to reduce latency
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


s.bind(('0.0.0.0', 25565))
s.listen()



server = Server("PyCube Test Server","Welcome Traveller")

allocatedSlots = [0]*128
def findMinAvailableID():
    for i in range(128):
        if (server.allocatedSlots[i] == 0):
            server.allocatedSlots[i] = 1
            return i
            
    return -1
def processClient(playerID,conn,addr):

    buffer = b''
    packetID = None

    while True:
        
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            print("Connection has been terminated. Ending connection")
            conn.close()
            return

        if (data):
            buffer += data
        else:
            print("Connection has been terminated. Ending connection")
            conn.close()
            return
        
        if (buffer):
            packetID = int(buffer[0])
        else:
            packetID = None
        
        if (packetID == None):
            # We have receieved nothing here
            pass
        elif (packetID not in protocol.clientPacketDict.keys()):
            print("Invalid packet ID receieved: ",packetID)
            print("DEBUG buffer: ")
            protocol.disconnectPlayer(server,conn,"Server: Rejected invalid packet ID: "+str(packetID))
            print(buffer)
            return

        while (len(buffer) > 0 and protocol.clientPacketLengths[packetID] <= len(buffer)):
            #print("Address: ", addr,"Packet ID: ",packetID,len(data))
            expectedLength = protocol.clientPacketLengths[packetID]
            packetData = buffer[0:expectedLength]
            buffer = buffer[expectedLength:]
            
            protocol.clientPacketDict[packetID](playerID,packetData,conn,server)

            if (len(buffer) > 0):
                packetID = int(buffer[0])

                if (packetID not in protocol.clientPacketDict.keys()):
                    print("Invalid packet ID received: ",packetID)
                    print("DEBUG buffer: ")
                    print(buffer)
                    protocol.disconnectPlayer(server,conn,"Server: Rejected invalid packet ID: "+str(packetID))
                    return


def pingEveryone(server):

    connList = server.connList
    
    
    while True:
        for p in range(128):
            if (connList[p] != None):
                print("PING "+str(p))
                protocol.ping(server, connList[p])
                    
        time.sleep(5)



if __name__ == "__main__":    
    pingThread = threading.Thread(target=pingEveryone, args=(server,))
    pingThread.start()

    heartBeatThread = threading.Thread(target=heartbeat.heartbeat, args=(server.SERVER_NAME, 25565, 10))
    heartBeatThread.start()



    globalThread = threading.Thread(target=server.globalThread,args=(server, ))
    globalThread.start()
    while True:
        conn, addr = s.accept()
        
        playerID = findMinAvailableID()
        if (playerID < 0):
            continue
        server.connList[playerID] = conn
        server.addPlayerID("",playerID,conn)

        #workerThread = threading.Thread(target=server.workerThread,args=(server, playerID, ))
        #workerThread.start()

        t1 = threading.Thread(target=processClient,args=(playerID,conn,addr))
        print("New connection from address:",addr," with player ID: ", playerID)
        t1.start()

    print("Ending main thread")
    