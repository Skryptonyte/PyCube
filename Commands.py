
import protocol

def kickPlayer(server, playerID, conn, args):
    if (len(args) != 2):
        protocol.serverMessage(server, conn, "Syntax: /kick <player>")
    elif (args[1] not in server.playerNameData.keys()):
        protocol.serverMessage(server, conn, "Player not found!")
    else:
        targetID = server.playerNameData[args[1]].playerID
        protocol.disconnectPlayer(server,server.connList[targetID],"You have been kicked for being a sussy baka.")


def saveWorld(server, playerID, conn, args):
    world = server.playerData[playerID].world
    protocol.serverMessageBroadcast(server,server.connList,"Saving World: "+world.fileName)
    world.saveWorld()
    protocol.serverMessageBroadcast(server, server.connList,"Saving Complete..")

def opPlayer(server, playerID, conn, args):
    if (len(args) != 2):
        protocol.serverMessage(server, conn, "Syntax: /op <player>")
    elif (args[1] not in server.playerNameData.keys()):
        protocol.serverMessage(server, conn, "Player not found!")
    else:
        targetID = server.playerNameData[args[1]].playerID
        targetPlayer = server.playerNameData[args[1]]
        protocol.serverMessage(server, server.playerNameData[args[1]].conn, "You are now OP")
        protocol.updateUserType(server, server.connList[targetID],0x64)

        targetPlayer.opLevel = 0x64

def deopPlayer(server, playerID, conn, args):
    if (len(args) != 2):
        protocol.serverMessage(server, conn, "Syntax: /deop <player>")
    elif (args[1] not in server.playerNameData.keys()):
        protocol.serverMessage(server, conn, "Player not found!")
    else:
        targetID = server.playerNameData[args[1]].playerID
        protocol.serverMessage(server, server.playerNameData[args[1]].conn, "You are no longer OP")
        protocol.updateUserType(server, server.connList[targetID],0x00)

def tpPlayer(server, playerID, conn, args):
    if (len(args) not in [2,4]):
        protocol.serverMessage(server, conn, "Syntax: /tp playerName or /tp <X> <Y> <Z>")
    else:
        if (len(args) == 2):
            targetPlayer = args[1]
            if (args[1] not in server.playerNameData.keys()):
                protocol.serverMessage(server, conn, "Player doesn't exist")
            else:
                targetPlayer = server.playerNameData[args[1]]
                if (targetPlayer.world != server.playerData[playerID].world):
                    protocol.serverMessage(server, conn, "Player is in different world")
                protocol.positionUpdate(server, conn, -1, targetPlayer.positionX, targetPlayer.positionY, targetPlayer.positionZ, 0,0)
        elif len(args) == 4:
            x = 0
            y = 0
            z = 0

            try:
                x = int(args[1])
                y = int(args[2])
                z = int(args[3])
            except:
                protocol.serverMessage(server, conn, "Coordinates must be integers")
                return

            boundCheckX = x >= 0 and x<=server.playerData[playerID].world.worldX 
            boundCheckY = y >= 0 and x<=server.playerData[playerID].world.worldY 
            boundCheckZ = z >= 0 and x<=server.playerData[playerID].world.worldZ 

            if (not (boundCheckX and boundCheckY and boundCheckZ)):
                protocol.serverMessage(server,conn,"Out of Bounds!")
            else:
                protocol.positionUpdate(server, conn, -1, x<<5, y<<5, z<<5, 0,0)


def announce(server, playerID, conn, args):
    message = ' '.join(args[1:])
    print("Announcement:",message)
    protocol.serverMessageBroadcast(server,server.connList,"&2"+message,100)

def stopServer(server, playerID, conn, args):
    import os
    print("Stopping server")
    for i in server.playerData:
        protocol.disconnectPlayer(server,server.playerData[i].conn,"Server closed")
    os._exit(0)
    server.mustExit = True
def fallbackCommand(server, playerID, conn, args):
    protocol.serverMessage(server, conn, "&cNo such command: "+args[0])

def maps(server, playerID, conn, args):
    protocol.serverMessage(server, conn,"&2Available Maps:")
    for m in server.worlds.keys():
        protocol.serverMessage(server, conn, "&b"+m)

def gotoWorld(server, playerID, conn, args):
    if (len(args) != 2):
        protocol.serverMessage(server, conn,"Syntax: /goto <mapName>")
    else:
        if (server.worlds.get(args[1],None)):
            protocol.serverMessage(server, conn, "Moving into another world")
            world = server.worlds.get(args[1],None)
            protocol.loadWorld(server,conn,world,playerID)
        else:
            protocol.serverMessage(server, conn, "Map not found")
commandTable = {"/kick": kickPlayer,
                "/save": saveWorld,
                "/op": opPlayer,
                "/deop": deopPlayer,
                "/tp": tpPlayer,
                "/announce":announce,
                "/maps": maps,
                "/goto": gotoWorld,
                "/stop": stopServer}
