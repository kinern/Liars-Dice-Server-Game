#Liar's Dice Server

import asyncio
import websockets
import uuid
import json


serverMessages = {
    setup: '{"action":"action", "id":id}', #Pass id to the client
    joined: '{"action":"joined", name:name}', #Broadcast new player name to clients
    start: '{"action":"start", game_id}', #Broadcast game has started to players
    nextTurn: '{action:next_turn, players:{name1, name2, name3}, current_id, prev_bid}', #Get new round info to all players
    bid: '{action:bid, player, new_bid}', #Broadcast result of current player bidding
    challenge: '{action:challenge, prev_bid, challenge_player, bid_player, result, result_dice}', #Broadcast result of current player challenging, round ends
    endGame: '{action:end_game, winner:name, winner_id}' #Broadcast the game has ended and winner
}


def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


#Globals
players = []
inGamePlayers = []
gameStarted = False
prevBid = {quantity: 0, value: 0}


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

def handleChallenge(response):
    if response["id"] == currentTurnId:
        return ''

#Start websocket server with asyncio
start_server = websockets.serve(response, 'localhost', 1234)
asyncio.get_event_loop().run_until_complete(gameLoop())
asyncio.get_event_loop().run_forever()

