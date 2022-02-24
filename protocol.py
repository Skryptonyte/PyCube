import struct
import time
import gzip

import Commands

def sendMessage(conn, server,data):
    playerID = server.connList.index(conn)
    server.playerData[playerID].messageQueue.put((playerID, data))
playerCount = 0
def ping(server,conn):
    data = struct.pack('!B',0x01)
    #print("PING sent")
    sendMessage(conn, server, data)
    #sendMessage(conn, server, data)

def levelInitialize(server,conn):
    data = struct.pack('!B',0x02)
    #print("INITIALIZE LEVEL")
    try:
        sendMessage(conn, server, data)
    except:
        pass


def levelChunk(server,conn,world):
    packetID = struct.pack('!B',0x03)
    percentComplete = struct.pack('!B',0)

    worldData = gzip.compress(struct.pack('!i',world.worldX*world.worldY*world.worldZ) + world.world[18:])
    
    index = 0
    while (index < len(worldData)):
        chunkData = worldData[index:index+1024]
        chunkLengthInt = len(chunkData)
        
        chunkData = chunkData + struct.pack('!B',0)*(1024-len(chunkData))

        chunkLength = struct.pack('!h',chunkLengthInt)
        data = packetID + chunkLength + chunkData + percentComplete
        #print("LOAD CHUNK OF SIZE: ",len(data))
        #print("-- DATA:",(data),chunkLengthInt)
        try:
            sendMessage(conn, server, data)
        except:
            print("[WARN]: Failed to send world data to somebody")
            return
        index+= 1024
        

def levelFinalize(server,conn,x,y,z):
    packetID = struct.pack('!B',0x04)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    data = packetID + X + Y + Z
    #print("FINALIZE LEVEL")
    print(data)
    try:
        sendMessage(conn, server, data)
    except:
        pass

def loadWorld(server, conn, world, playerID):
    print("Loading world "+ world.fileName +"for player: "+str(playerID))
    username = server.playerData[playerID].playerName
    worldX = world.worldX
    worldZ = world.worldZ
    worldY = world.worldY
    
    spawnX = world.spawnX
    spawnZ = world.spawnZ
    spawnY = world.spawnY
    
    heading = world.heading
    pitch = world.pitch

    despawnPlayerBroadcast(server, server.connList,playerID)
    server.playerData[playerID].world = world

    levelInitialize(server,conn)
    levelChunk(server,conn, world)
    levelFinalize(server, conn,worldX, worldY, worldZ)
    positionUpdate(server, conn,-1,spawnX,spawnY,spawnZ,heading,pitch)

    spawnPlayer(server,conn,-1,username,spawnX,spawnY,spawnZ,heading,pitch)
    for p in range(128):
        try:
            if (server.connList[p] and p != playerID and server.playerData[p].world == server.playerData[playerID].world):
                spawnPlayer(server,server.connList[p],playerID,username,spawnX,spawnY,spawnZ,heading,pitch)     # Spawn player in everyone else's clients
                spawnPlayer(server,conn,p,server.playerData[p].playerName,spawnX,spawnY,spawnZ,heading,pitch)   # Spawn all players in our client
        except Exception as e:
                pass

    positionUpdate(server,conn,-1,spawnX,spawnY,spawnZ,heading,pitch)
    print("Loading complete")
            
def spawnPlayer(server,conn,playerID,playerName,x,y,z,heading,pitch):
    global playerCount
    
    packetID = struct.pack('!B',0x07)
    player = struct.pack('!b',playerID)
    
    playerName = playerName[0:64]
    playerNameConv = bytes(playerName+" "*(64 - len(playerName)),'utf-8')
    
    print(x,y,z)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    H = struct.pack('!B',heading)
    P = struct.pack('!B',pitch)
    
    data = packetID + player + playerNameConv + X+Y+Z+H+P
    #print("SPAWN PLAYER:",playerName,"with ID:",player)
    print(data)
    try:
        sendMessage(conn, server, data)
    except:
        pass
    
def positionUpdate(server, conn,playerID, x, y, z, heading, pitch):

    packetID = struct.pack('!B',0x08)
    playeridconv = struct.pack('!b',playerID)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    H = struct.pack('!B',heading)
    P = struct.pack('!B',pitch)
    
    data = packetID + playeridconv + X + Y + Z + H + P
    try:
        sendMessage(conn, server, data)
    except:
        pass




def despawnPlayer(server, conn,playerID):
    packetID = struct.pack('!B',0x0c)
    playerID = struct.pack('!b',playerID)
    
    data = packetID + playerID
    try:
        sendMessage(conn, server, data)
    except:
        pass
    
def despawnPlayerBroadcast(server, connList, playerID):
    print("BROADCAST DESPAWN")
    for p in range(128):
        if (connList[p] != None):
            despawnPlayer(server,connList[p],playerID)
            



def serverMessage(server, conn, message):
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',0xff)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    

    data = packetID+unused+message
    try:
        sendMessage(conn, server, data)
    except:
        pass
    
def serverMessageBroadcast(server, connList, message):
            
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',0xff)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    
    data = packetID+unused+message
    for p in range(128):
        if (connList[p] != None):
            try:
                sendMessage(connList[p], server, data)
            except:
                pass

def serverBlockUpdate(server,conn, x,y,z,block):
    packetID = struct.pack('!B',0x06)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    B = struct.pack('!B',block)
    
    data = packetID + X + Y + Z + B
    try:
        sendMessage(conn, server, data)
    except:
        pass
    
def serverBlockUpdateBroadcast(server, sendingID, connList, x, y, z, block):
    for p in range(128):
        if (connList[p] != None and server.playerData[sendingID].world == server.playerData[p].world):
            serverBlockUpdate(server,connList[p],x,y,z,block)
                
                
def disconnectPlayer(server, conn,disconnectReason):
    packetID = struct.pack('!B',0x0e)
    disconnectReason = bytes(disconnectReason + " "*(64-len(disconnectReason)),'utf-8')
    
    data = packetID + disconnectReason
    try:
        sendMessage(conn, server, data)
    except:
        pass


def updateUserType(server, conn, userType):
    packetID = struct.pack('!B',0x0f)
    userType = struct.pack('!B',userType)
    
    data = packetID + userType
    try:
        sendMessage(conn, server, data)
    except:
        pass

serverPacketDict = {0x01: ping,
                    0x02: levelInitialize,
                    0x03: levelChunk,
                    0x04: levelFinalize,
                    0x07: spawnPlayer,
                    0x08: positionUpdate,
                    0x0c: despawnPlayer,
                    0x0d: serverMessage,
                    0x0e: disconnectPlayer
                    }

def playerIdentification(playerID,data,conn,server):

    world = server.worlds["world"]
    connList = server.connList
        
    packetID = data[0]
    protocolVersion = data[1]
    username = (data[2:66]).decode("utf-8").strip()
    verificationKey = (data[66:130]).decode("utf-8").strip()

    if (username in server.playerNameData.keys()):
        disconnectPlayer(server, conn,"Already logged in")
        return
    
    #server.addPlayerID(username,playerID, conn)
    #print(data)
    server.playerData[playerID].playerName = username
    server.playerNameData[username] = server.playerData[playerID]

    packetIDS = bytes((0,))
    serverProtocol = bytes((7,))
    serverName = bytes(server.SERVER_NAME + " "*(64 - len(server.SERVER_NAME)),'utf-8')
    serverMOTD = bytes(server.SERVER_MOTD + " "*(64 - len(server.SERVER_MOTD)),'utf-8')
    userType = bytes((0,))


    newMessage = packetIDS + serverProtocol + serverName +serverMOTD + userType
    print(newMessage)
    sendMessage(conn, server, newMessage)

    loadWorld(server,conn,world,playerID)
    serverMessageBroadcast(server,connList, username + " has joined the world.")

def clientPositionUpdate(playerID,data, conn, server):

    world = server.playerData[playerID].world
    connList = server.connList
    
    packetID = struct.unpack('!B',data[0:1])[0]
    playerIDr = struct.unpack('!b',data[1:2])[0]
    x = struct.unpack('!h',data[2:4])[0]
    y = struct.unpack('!h',data[4:6])[0]
    z = struct.unpack('!h',data[6:8])[0]
    h = struct.unpack('!B',data[8:9])[0]
    p = struct.unpack('!B',data[9:10])[0]
    
    #print("Player ID:",playerIDr,"POSITION UPDATE:",x>>5,y>>5,z>>5)

    server.playerData[playerID].setPosition(x,y,z)
    for p in range(128):
        try:
            if (connList[p] and p != playerID and server.playerData[playerID].world == server.playerData[p].world):
                positionUpdate(server,connList[p],playerID,x,y,z,h,p)
        except:
            pass
    
def clientBlockUpdate(playerID,data, conn, server):

    world = server.playerData[playerID].world
    connList = server.connList
    
    packetID = struct.unpack('!B',data[0:1])
    X = struct.unpack('!h',data[1:3])[0]
    Y = struct.unpack('!h',data[3:5])[0]
    Z = struct.unpack('!h',data[5:7])[0]
    mode = struct.unpack('!B',data[7:8])[0]
    block = struct.unpack('!B',data[8:9])[0]

    newBlock = 0
    
    if (mode == 1):
        newBlock = block
    
    serverBlockUpdateBroadcast(server,playerID, connList,X,Y,Z,newBlock)
    world.setBlock(X,Y,Z,mode,newBlock)
    
    
def clientMessage(playerID,data, conn, server):

    world = server.playerData[playerID].world
    connList = server.connList
    
    packetID = struct.unpack('!B',data[0:1])[0]
    playerIDr = struct.unpack('!b',data[1:2])[0]
    message = (data[2:66]).decode("utf-8").strip()
    print("Message:",message)
    print(len(message))
    
    username = server.playerData[playerID].playerName
    print("Neg: ",server.playerData[playerID].playerName)
    if (message[0]  != '/'):
        message = "&f"+username + ": " + message

        serverMessageBroadcast(server,connList,message)
        if (len(message) > 64):
            message2 = "&f"+message[64:]
            serverMessageBroadcast(server, connList,message2)
        

    else:
        args = message.split(" ")
        try:
            Commands.commandTable.get(args[0],Commands.fallbackCommand)(server, playerID, conn, args)
        except Exception as e:
            print("Exception occurred during player command: "+str(e))
    
    

    

clientPacketDict = {0x0 : playerIdentification, 0x05:clientBlockUpdate,0x8: clientPositionUpdate, 0xd: clientMessage}
clientPacketLengths = {0x0: 131, 0x05: 9, 0x08: 10, 0x0d:66}
