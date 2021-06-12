#Liar's Dice Server

import asyncio
import websockets
import uuid
import json
import random


#serverMessages = {
#    setup: '{"action":"action", "id":id}', #Pass id to the client
#    joined: '{"action":"joined", name:name}', #Broadcast new player name to clients
#    start: '{"action":"start", game_id}', #Broadcast game has started to players
#    nextTurn: '{action:next_turn, players:{name1, name2, name3}, current_id, prev_bid}', #Get new round info to all players
#    bid: '{action:bid, player, new_bid}', #Broadcast result of current player bidding
#    challenge: '{action:challenge, prev_bid, challenge_player, bid_player, result, result_dice}', #Broadcast result of current player challenging, round ends
#    endGame: '{action:end_game, winner:name, winner_id}' #Broadcast the game has ended and winner
#}

#Globals
players = []
userWebsockets = []
MAX_DICE = 5
MAX_PLAYERS = 3
game = None


class Player:
    def __init__(self, name, id, ws):
        self.name = name
        self.id = id
        self.websocket = ws
        self.numDice = MAX_DICE
        self.dice = createDice(self.numDice)
    
    def createDice(self):
        dice = []
        for x in range(self.numDice-1):
            dice.append(random.randint(1,6))
        return dice
    

def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


def getPlayerNames():
    names = []
    for player in inGamePlayers:
        names.append(player["name"])
    return names




class Game:
    def __init__(self):
        self.currentTurn = 0
        self.players = players
        self.prevBid = {"quantity": 0, "value":0}


    async def nextTurn(self):
        if self.currentTurn >= len(self.players):
            self.currentTurn = 0
        else:
            self.currentTurn = self.currentTurn + 1
        playerNames = getPlayerNames()

        #Todo: loop with dices for each player
        for player in self.players:
            jsonMsg = json.dumps({
                    "action": "next_turn", 
                    "players": playerNames, 
                    "prev_bid": prevBid,
                    "dice": player["dice"],
                    "turn_id": players[currentTurn]["id"], 
                    "turn_name": players[currentTurn]["name"]
                    })
            await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
            await asyncio.sleep(5)


    async def updateBid(self, response):
        if response["id"] == self.getCurrentTurnId():
            self.prevBid["quantity"] = response["bid"]["quantity"]
            self.prevBid["value"] = response["bid"]["value"]
            jsonMsg = json.dumps({
                "action":"bid",
                "player": response["id"],
                "new_bid" : {"quantity" : response["bid"]["quantity"], "value" : response["bid"]["value"]}
            })
            await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
            await asyncio.sleep(5)
            self.nextTurn()


    def handleChallenge(self, response):
        if response["id"] == self.getCurrentTurnId():
            self.challenge()
            self.endRound()


    def getCurrentTurnId(self):
        return self.players[self.currentTurn]["id"]


    async def challenge(self):
        playerLen = len(self.players)
        prevIndex =  playerLen-1 if self.currentTurn == 0 else self.currentTurn-1
        challengeRedult = correctBid()
        if challengeResult:
            if self.currentTurn == playerLen:
                self.players[0].numDice - 1
            else:
                self.players[self.currentTurn-1].numDice - 1
        else:
            if self.currentTurn == 0:
                self.players[0].numDice - 1
            else:
                self.players[self.currentTurn-1].numDice - 1
        jsonMsg = json.dumps({
            "action":"challenge",
            "challenge_player": self.players[self.currentTurn]["name"],
            "bid_player": self.players[prevIndex]["name"],
            "result": challengeResult,
            "result_dice": getDiceTotals()
        })
        await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
        await asyncio.sleep(5)


    def getDiceTotals(self):
        diceTotals = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for player in self.players:
            for die in player.dice:
                diceTotals[die] = diceTotals[die]+1
        return diceTotals


    def correctBid(self):
        diceTotals = getDiceTotals()
        return  diceTotals[self.prevBid["value"]] >= self.prevBid["quantity"]


    def endRound(self):
        for player in self.players:
            if len(player["dice"]) == 0:
                self.players.remove(player)
        if len(self.players) == 1:
            endGame()
        else:
            nextTurn() 


    async def endGame(self):
        jsonMsg = json.dumps({
            "action": "endgame",
            "winner": self.players[0]["name"],
            "winner_id": self.player[0]["id"]
        })
        await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])


#Main game loop
async def main(websocket, path):

    print('== Server Started ==')

    response = await websocket.recv()
    response = parseMsg(response)

    if response.has_key("action"):
        if response["action"] == "join":

            playerId = playerJoin(response, websocket)
            await websocket.send(json.dumps({"id": playerId}))

            if len(players) >= MIN_PLAYERS:
                game = Game(players)
                game.nextTurn()

        elif response["action"] == "bid":
            game.updateBid(response)
        elif response["action"] == "challenge":
            game.handleChallenge(response)


async def playerJoin(response, ws):
    newId = uuid.uuid1()
    players.append(Player(response["name"], newId, ws))
    userWebsockets.add(ws)
    jsonMsg = json.dumps({
        "action":"joined",
        "player": response["name"]
    })
    await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
    return newId

#Start websocket server with asyncio
start_server = websockets.serve(main, 'localhost', 1234)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

