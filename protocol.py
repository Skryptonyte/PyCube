import struct
import time
import gzip
import zlib
import Commands

def sendMessage(conn, server,data):
    playerID = server.connList.index(conn)
    #server.playerData[playerID].messageQueue.put((playerID, data))
    server.messageQueue.put((playerID, data))
playerCount = 0
def ping(server,conn):
    data = struct.pack('!B',0x01)
    #print("PING sent")
    sendMessage(conn, server, data)
    #sendMessage(conn, server, data)

def levelInitialize(server,conn,playerID):
    world = server.playerData[playerID].world
    data = struct.pack('!B',0x02)

    # Check if client supports FastMap, if so append an int containing worldsize
    if (server.playerData[playerID].CPE.get("FastMap",0)):
        print("Intialize FastMap transfer")
        data += struct.pack('!i',world.worldX*world.worldY*world.worldZ)
    #print("INITIALIZE LEVEL")
    try:
        sendMessage(conn, server, data)
    except:
        pass


def levelChunk(playerID, server,conn,world):
    packetID = struct.pack('!B',0x03)
    percentComplete = struct.pack('!B',0)

    worldData = None

    if (server.playerData[playerID].CPE.get("FastMap",0)):
        print("Level Load with FastMap enabled")
        compress = zlib.compressobj(-1, zlib.DEFLATED, -15)
        worldData = compress.compress(world.world[18:])
        worldData += compress.flush()

    else:
        print("Level Load with FastMap disabled")
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

    levelInitialize(server,conn,playerID)
    levelChunk(playerID,server,conn, world)

    if (server.playerData[playerID].CPE.get("EnvColors",0)):
        CPE_envSetColor(playerID, conn, server, 0, 255, 0, 0)

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
    
    print("Spawn:",x,y,z)
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
            



def serverMessage(server, conn, message, messageType=0x0):
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',messageType)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    

    data = packetID+unused+message
    try:
        sendMessage(conn, server, data)
    except Exception as e:
        print(e)
        pass
    
def serverMessageBroadcast(server, connList, message,messageType=0x0):
            
    packetID = struct.pack('!B',0x0d)
    unused = struct.pack('!B',messageType)
    message = bytes(message[0:64] + " "*(64-len(message)),'utf-8')
    
    data = packetID+unused+message
    for p in range(128):
        if (connList[p] != None):
            try:
                sendMessage(connList[p], server, data)
            except Exception as e:
                print(e)
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
    except Exception as e:
        print(e)
        pass


def updateUserType(server, conn, userType):
    packetID = struct.pack('!B',0x0f)
    userType = struct.pack('!B',userType)
    
    data = packetID + userType
    try:
        sendMessage(conn, server, data)
    except:
        pass

def serverIdentification(playerID, conn, server, motd):

    world = server.worlds["world"]
    connList = server.connList

    packetIDS = bytes((0,))
    serverProtocol = bytes((7,))
    serverName = bytes(server.SERVER_NAME + " "*(64 - len(server.SERVER_NAME)),'utf-8')
    serverMOTD = bytes(motd + " "*(64 - len(motd)),'utf-8')
    userType = bytes((0,))


    newMessage = packetIDS + serverProtocol + serverName +serverMOTD + userType
    sendMessage(conn, server, newMessage)



def playerIdentification(playerID,data,conn,server):

    world = server.worlds["world"]
    connList = server.connList
        
    packetID = data[0]
    protocolVersion = data[1]
    username = (data[2:66]).decode("utf-8").strip()
    verificationKey = (data[66:130]).decode("utf-8").strip()
    padding = int(data[130])
    if (username in server.playerNameData.keys()):
        disconnectPlayer(server, conn,"Already logged in")
        return
    
    #server.addPlayerID(username,playerID, conn)
    #print(data)
    server.playerData[playerID].playerName = username
    server.playerNameData[username] = server.playerData[playerID]

    # Detect CPE
    if (padding == 0x42):
        print("Note: Client supports CPE")
        extInfoPacketServer(playerID, conn, server, 2)
        for cpeExtName in server.CPE:
            extEntryPacketServer(playerID,conn,server, cpeExtName,server.CPE[cpeExtName])
    else:
        serverIdentification(playerID, conn, server,server.SERVER_MOTD)
        loadWorld(server,conn,world,playerID)
        serverMessageBroadcast(server,connList, server.playerData[playerID].playerName + " has joined the world.")
    """
    packetIDS = bytes((0,))
    serverProtocol = bytes((7,))
    serverName = bytes(server.SERVER_NAME + " "*(64 - len(server.SERVER_NAME)),'utf-8')
    serverMOTD = bytes(server.SERVER_MOTD + " "*(64 - len(server.SERVER_MOTD)),'utf-8')
    userType = bytes((0,))


    newMessage = packetIDS + serverProtocol + serverName +serverMOTD + userType
    sendMessage(conn, server, newMessage)

    loadWorld(server,conn,world,playerID)
    serverMessageBroadcast(server,connList, username + " has joined the world.")
    """
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
    

    X = server.playerData[playerID].positionX
    Y = server.playerData[playerID].positionY
    Z = server.playerData[playerID].positionZ

    if (x == X and y == Y and z == Z):
        return
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
    
 # CPE Packets

def extInfoPacketServer(playerID, conn, server, extCount):
    packetID = struct.pack('!B',0x10)
    serverInfo =  bytes(server.SERVER_VERSION + " "*(64 - len(server.SERVER_VERSION)),'utf-8')
    extensionCount = struct.pack('!h',extCount)

    packet = packetID + serverInfo + extensionCount

    sendMessage(conn,server,packet)

def extEntryPacketServer(playerID, conn, server, extName, version):
    packetID = struct.pack('!B',0x11)
    extName = bytes(extName + " "*(64 - len(extName)),'utf-8')
    extVersion = struct.pack('!I',version)

    packet = packetID + extName + extVersion
    sendMessage(conn,server,packet)

def extInfoPacketClient(playerID, data, conn, server):
    packetID = struct.unpack('!B', data[0:1])
    serverInfo = data[1:65]
    extensionCount = struct.unpack('!h',data[65:67])[0]

    server.playerData[playerID]._extensionsLeft = extensionCount

def extEntryPacketClient(playerID, data, conn, server):
    packetID = struct.unpack('!B', data[0:1])
    extName = data[1:65]
    version = struct.unpack('!I',data[65:69])[0]

    #print("Client reports CPE Extension:",extName.decode('utf-8'),"Version:",version)
    server.playerData[playerID]._extensionsLeft -= 1

    trimmedName = extName.decode('utf-8').strip()
    if (server.CPE.get(trimmedName,0) == version):
        server.playerData[playerID].CPE[trimmedName] = version
        print("Mutually Supported Extension:",trimmedName,"Version:",version)
    if (server.playerData[playerID]._extensionsLeft == 0):
        print("Finished CPE Handshake")
        serverIdentification(playerID, conn, server,server.SERVER_MOTD)

        world = server.worlds["world"]
        connList = server.connList

        loadWorld(server,conn,world,playerID)
        serverMessageBroadcast(server,connList, server.playerData[playerID].playerName + " has joined the world.")

        serverMessage(server,conn,server.SERVER_VERSION,1)
        serverMessage(server,conn,"&cVery Unstable",2)
        
        CPE_clickDistance(playerID, conn, server, 320)
        CPE_customBlocks(playerID, conn, server)

        server.playerData[playerID]._extensionsLeft -= 1



def CPE_clickDistance(playerID, conn, server, clickDist):
    packetID = struct.pack('!B',0x12)
    clickDist = struct.pack('!h',clickDist)

    packet = packetID + clickDist
    sendMessage(conn,server,packet)

def CPE_customBlocks(playerID, conn, server):
    packetID = struct.pack('!B', 0x13)
    supportLevel = struct.pack('!B',0x1)

    packet = packetID + supportLevel
    sendMessage(conn,server,packet)

def CPE_customBlocks_client(playerID, data, conn, server):
    packetID = struct.unpack('!B', data[0:1])
    supportLevel = struct.unpack('!B',data[1:2])

def CPE_playerClicked_client(playerID, data, conn, server):
    print("Player Click (Stubbed)")
    packetID = struct.unpack('!B',data[0:1])

def CPE_envSetColor(playerID, conn, server, type, r, g, b):
    packetID = struct.pack('!B',0x19)
    type = struct.pack('!B',type)
    red = struct.pack('!h',r)
    green = struct.pack('!h',g)
    blue = struct.pack('!h',b)

    packet = packetID + type+red + green + blue 

    sendMessage(conn,server,packet)

def CPE_twoWayPing_client(playerID, data, conn, server):
    packetID = struct.unpack('!B',data[0:1])
    direction = struct.unpack('!B',data[1:2])
    counter = struct.unpack('!h',data[2:4])


    retPacket = data[0:1] + struct.pack('!B',0) + data[2:4]
    print("Two way ping")
    sendMessage(conn,server,retPacket)
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
    

clientPacketDict = {0x0 : playerIdentification, 
                    0x05:clientBlockUpdate,
                    0x8: clientPositionUpdate, 
                    0xd: clientMessage,
                    
                    0x10: extInfoPacketClient,
                    0x11: extEntryPacketClient,
                    0x13: CPE_customBlocks_client,
                    0x22: CPE_playerClicked_client,
                    0x2b: CPE_twoWayPing_client
                    }
clientPacketLengths = {0x0: 131, 0x05: 9, 0x08: 10, 0x0d:66,
                    0x10:67, 0x11: 69,0x13: 2, 0x22:15,0x2b: 4}
