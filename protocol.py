import struct
import time
import gzip

SERVER_NAME = "&4TEST_SERVER"
SERVER_MOTD = "&aYER MUM GAY"

playerCount = 0
def ping(conn):
    data = struct.pack('!B',0x01)
    print("PING sent")
    conn.sendall(data)

def levelInitialize(conn):
    data = struct.pack('!B',0x02)
    print("INITIALIZE LEVEL")
    conn.sendall(data)


def levelChunk(conn,world):
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
        conn.sendall(data)
        
        index+= 1024
        

def levelFinalize(conn,x,y,z):
    packetID = struct.pack('!B',0x04)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    data = packetID + X + Y + Z
    print("FINALIZE LEVEL")
    print(data)
    conn.sendall(data)

def spawnPlayer(conn,playerID,playerName,x,y,z,heading,pitch):
    global playerCount
    
    packetID = struct.pack('!B',0x07)
    player = struct.pack('!b',playerID)
    
    playerNameConv = bytes(playerName+" "*(64 - len(playerName)),'utf-8')
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    H = struct.pack('!B',heading)
    P = struct.pack('!B',pitch)
    
    data = packetID + player + playerNameConv + X+Y+Z+H+P
    print("SPAWN PLAYER:",playerName,"with ID:",player)
    print(data)
    conn.sendall(data)
    
def positionUpdate(conn,playerID, x, y, z, heading, pitch):

    packetID = struct.pack('!B',0x08)
    playeridconv = struct.pack('!b',playerID)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    H = struct.pack('!B',heading)
    P = struct.pack('!B',pitch)
    
    data = packetID + playeridconv + X + Y + Z + H + P
    conn.sendall(data)


def despawnPlayer(conn,playerID):
    packetID = struct.pack('!B',0x0c)
    playerID = struct.pack('!b',playerID)
    
    data = packetID + playerID
    conn.sendall(data)
    
def despawnPlayerBroadcast(connList, playerID):
    for p in range(128):
        if (connList[p] != None):
            try:
                despawnPlayer(connList[p],playerID)
            except:
                pass
            



def serverMessage(conn, message):
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',0xff)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    
    data = packetID+unused+message
    conn.sendall(data)
    
def serverMessageBroadcast(connList, message):
            
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',0xff)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    
    data = packetID+unused+message
    for p in range(128):
        if (connList[p] != None):
            try:
                connList[p].sendall(data)
            except:
                pass

def serverBlockUpdate(conn, x,y,z,block):
    packetID = struct.pack('!B',0x06)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    B = struct.pack('!B',block)
    
    data = packetID + X + Y + Z + B
    conn.sendall(data)
    
def serverBlockUpdateBroadcast(connList, x, y, z, block):
    packetID = struct.pack('!B',0x06)
    X = struct.pack('!h',x)
    Y = struct.pack('!h',y)
    Z = struct.pack('!h',z)
    B = struct.pack('!B',block)
    
    data = packetID + X + Y + Z + B
    for p in range(128):
        if (connList[p] != None):
            try:
                connList[p].sendall(data)
            except e:
                print("Something happened while setting block")
                
                
def disconnectPlayer(conn,disconnectReason):
    packetID = struct.pack('!B',0x0e)
    disconnectReason = bytes(disconnectReason + " "*(64-len(disconnectReason)),'utf-8')
    
    data = packetID + disconnectReason
    conn.sendall(data)


def updateUserType(conn, userType):
    packetID = struct.pack('!B',0x0f)
    userType = struct.pack('!B',userType)
    
    data = packetID + userType
    conn.sendall(data)
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

playerIDToName = {}
playerNameToID = {}
def playerIdentification(connList,playerID,data,conn,world):


    worldX = world.worldX
    worldZ = world.worldZ
    worldY = world.worldY
    
    spawnX = world.spawnX
    spawnZ = world.spawnZ
    spawnY = world.spawnY
    
    heading = world.heading
    pitch = world.pitch
    
    

    
    print(spawnX, spawnY, spawnZ)
    
    packetID = data[0]
    protocolVersion = data[1]
    username = (data[2:66]).decode("utf-8").strip()
    verificationKey = (data[66:130]).decode("utf-8").strip()

    playerIDToName[playerID] = username
    playerNameToID[username] = playerID
    
    print(data)

    packetIDS = bytes((0,))
    serverProtocol = bytes((data[1],))
    serverName = bytes(SERVER_NAME + " "*(64 - len(SERVER_NAME)),'utf-8')
    serverMOTD = bytes(SERVER_MOTD + " "*(64 - len(SERVER_MOTD)),'utf-8')
    userType = bytes((0,))

    newMessage = packetIDS + serverProtocol + serverName +serverMOTD + userType
    print(newMessage)
    conn.sendall(newMessage)
    levelInitialize(conn)
    levelChunk(conn,world)
    levelFinalize(conn,worldX,worldY, worldZ)
    
                
    spawnPlayer(conn,-1,username,spawnX,spawnY,spawnZ,heading,pitch)
    serverMessageBroadcast(connList, username + " has joined the game.")
    for p in range(128):
        try:
            if (connList[p] and p != playerID):
                spawnPlayer(connList[p],playerID,username,spawnX,spawnY,spawnZ,heading,pitch)
                spawnPlayer(conn,p,playerIDToName[p],spawnX,spawnY,spawnZ,heading,pitch)
        except:
            pass
            
    
    positionUpdate(conn,-1,spawnX,spawnY,spawnZ,heading,pitch)


def clientPositionUpdate(connList, playerID,data, conn, world):
    packetID = struct.unpack('!B',data[0:1])[0]
    playerIDr = struct.unpack('!b',data[1:2])[0]
    x = struct.unpack('!h',data[2:4])[0]
    y = struct.unpack('!h',data[4:6])[0]
    z = struct.unpack('!h',data[6:8])[0]
    h = struct.unpack('!B',data[8:9])[0]
    p = struct.unpack('!B',data[9:10])[0]
    
    #print("Player ID:",playerIDr,"POSITION UPDATE:",x>>5,y>>5,z>>5)

    for p in range(128):
        try:
            if (connList[p] and p != playerID):
                positionUpdate(connList[p],playerID,x,y,z,h,p)
        except:
            pass
    
def clientBlockUpdate(connList, playerID,data, conn, world):
    packetID = struct.unpack('!B',data[0:1])
    X = struct.unpack('!h',data[1:3])[0]
    Y = struct.unpack('!h',data[3:5])[0]
    Z = struct.unpack('!h',data[5:7])[0]
    mode = struct.unpack('!B',data[7:8])[0]
    block = struct.unpack('!B',data[8:9])[0]

    newBlock = 0
    
    if (mode == 1):
        newBlock = block
        
    serverBlockUpdateBroadcast(connList,X,Y,Z,newBlock)
    world.setBlock(X,Y,Z,mode,newBlock)
    
    
def clientMessage(connList, playerID,data, conn, world):
    packetID = struct.unpack('!B',data[0:1])[0]
    playerIDr = struct.unpack('!b',data[1:2])[0]
    message = (data[2:66]).decode("utf-8").strip()
    print("Message:",message)
    print(len(message))
    
    if (message[0]  != '/'):
        message = "&f"+playerIDToName[playerID] + ": " + message
        serverMessageBroadcast(connList, message)

    else:
        args = message.split(" ")
        print(args)
        if (args[0] == "/kick"):
            if (len(args) < 2):
                serverMessage(conn, "Syntax: /kick <player> reason")
            elif (args[1] not in playerNameToID.keys()):
                serverMessage(conn, "Player not found!")
            else:
                disconnectPlayer(connList[playerNameToID[args[1]]],"You have been kicked for being a sussy baka.")
        elif (args[0] == "/save"):
            serverMessage(conn,"Saving World...")
            world.saveWorld()
        elif (args[0] == "/op"):
            if (len(args) < 2):
                serverMessage(conn, "Syntax: /op <player>")
            elif (args[1] not in playerNameToID.keys()):
                serverMessage(conn, "Player not found!")
            else:
                updateUserType(connList[playerNameToID[args[1]]],0x64)

    
    

    

clientPacketDict = {0x0 : playerIdentification, 0x05:clientBlockUpdate,0x8: clientPositionUpdate, 0xd: clientMessage}
clientPacketLengths = {0x0: 131, 0x05: 9, 0x08: 10, 0x0d:66}
