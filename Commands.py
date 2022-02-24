
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
    if (not(len(args) == 2 )):
        protocol.serverMessage(server, conn, "Syntax: /tp playerName")
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

def fallbackCommand(server, playerID, conn, args):
    protocol.serverMessage(server, conn, "&cNo such command: "+args[0])

def maps(server, playerID, conn, args):
    protocol.serverMessage(server, conn,"&2Available Maps:")
    for m in server.world.keys():
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
                "/maps": maps,
                "/goto": gotoWorld}
