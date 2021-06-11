#Liar's Dice Server

import asyncio
import websockets
import uuid
import json


#serverMessages = {
#    setup: '{"action":"action", "id":id}', #Pass id to the client
#    joined: '{"action":"joined", name:name}', #Broadcast new player name to clients
#    start: '{"action":"start", game_id}', #Broadcast game has started to players
#    nextTurn: '{action:next_turn, players:{name1, name2, name3}, current_id, prev_bid}', #Get new round info to all players
#    bid: '{action:bid, player, new_bid}', #Broadcast result of current player bidding
#    challenge: '{action:challenge, prev_bid, challenge_player, bid_player, result, result_dice}', #Broadcast result of current player challenging, round ends
#    endGame: '{action:end_game, winner:name, winner_id}' #Broadcast the game has ended and winner
#}


def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


#Globals
players = []
inGamePlayers = []
gameStarted = False
prevBid = {quantity: 0, value: 0}
currentTurn = 0


def getPlayerNames():
    names = []
    for player in inGamePlayers:
        names.append(player["name"])
    return names


#Main game loop
async def gameLoop(websocket, path):

    #Get new clients and client actions
    response = await websocket.recv()
    response = parseMsg(response)

    if response.has_key("action"):
        if response["action"] == "join":
            #Store player info
            playerId = playerJoin(response)
            await websocket.send(json.dumps({"id": playerId}))
            if not gameStarted and len(players) >= MIN_PLAYERS:
                startNewGame()
        else if response["action"] == "bid":
            updateBid(response)
        else if response["action"] == "challenge":
            handleChallenge(response)
            #get challenge result, end round
            #end game if 1 player remaining, otherwise start new round


def nextTurn():
    if currentTurn >= len(players):
        currentTurn = 0
    else:
        currentTurn = currentTurn + 1
    playerNames = getPlayerNames()

    #Todo: loop with dices for each player
    for player in inGamePlayers:
        jsonMsg = json.dumps({
                "action": "next_turn", 
                "players": playerNames, 
                "prev_bid": prevBid,
                "dice": player["dice"]
                "turn_id": players[currentTurn]["id"], 
                "turn_name": players[currentTurn]["name"]
                })
        await websocket.send(player["websocket"], jsonMsg)


def startNewGame():
    inGamePlayers = players
    gameStarted = True


def playerJoin(response):
    newId = uuid.uuid1()
    players.append({name: response["name"], id: newId})
    return newId


def updateBid(response):
    if response["id"] == currentTurnId:
        prevBid["quantity"] = response["bid"]["quantity"]
        prevBid["value"] = response["bid"]["value"]
        nextTurn()


def handleChallenge(response):
    if response["id"] == currentTurnId:
        challenge()
        endRound()


def challenge():
    if correctBid():
        if currentTurn == len(players):
            players[0].removeDie()
        else:
            players[currentTurn-1].removeDie()
    else:
        if currentTurn == 0:
            players[0].removeDie()
        else:
            players[currentTurn-1].removeDie()
    

def correctBid():
    diceTotals = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for player in players:
        for die in player.dice:
            diceTotals[die] = diceTotals[die]+1
    return  diceTotals[previousBid["value"]] >= previousBid["quantity"]


def endRound():
    for player in players:
        if len(player["dice"]) == 0:
            players.remove(player)
    if len(players) == 1:
        endGame()
    else:
        nextTurn() 


#Start websocket server with asyncio
start_server = websockets.serve(response, 'localhost', 1234)
asyncio.get_event_loop().run_until_complete(gameLoop())
asyncio.get_event_loop().run_forever()

