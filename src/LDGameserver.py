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
MIN_PLAYERS = 2
game = None


class Player:
    def __init__(self, name, id, ws):
        self.name = name
        self.id = id
        self.websocket = ws
        self.numDice = MAX_DICE
        self.dice = self.createDice()
    
    def createDice(self):
        dice = []
        for x in range(self.numDice-1):
            dice.append(random.randint(1,6))
        return dice
    

def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr





class Game:
    def __init__(self):
        self.currentTurn = 0
        self.players = players
        self.prevBid = {"quantity": 0, "value":0}


    def getPlayerNames(self):
        names = []
        for player in self.players:
            names.append(player.name)
        return names

    async def nextTurn(self):
        if self.currentTurn >= len(self.players)-1:
            self.currentTurn = 0
        else:
            self.currentTurn = self.currentTurn + 1
        playerNames = self.getPlayerNames()

        #Todo: loop with dices for each player
        for player in self.players:
            jsonMsg = json.dumps({
                    "action": "next_turn", 
                    "players": playerNames, 
                    "prev_bid": self.prevBid,
                    "dice": player.dice,
                    "turn_id": players[self.currentTurn].id, 
                    "turn_name": players[self.currentTurn].name
                    })
            await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
            await asyncio.sleep(5)


    async def updateBid(self, response, websocket):
        if response["id"] == self.getCurrentTurnId():
            if self.validBid(response["new_bid"]):
                self.prevBid["quantity"] = response["new_bid"]["quantity"]
                self.prevBid["value"] = response["new_bid"]["value"]
                jsonMsg = json.dumps({
                    "action":"bid",
                    "player": self.getPlayerById(response["id"]).name,
                    "new_bid" : response["new_bid"]
                })
                await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])
                await asyncio.sleep(5)
                await self.nextTurn()
            else:
                #resend request to bidder
                jsonMsg = json.dumps({
                    "action": "bid_invalid",
                    "id": response["id"],
                    "prev_bid": self.prevBid
                })
                await websocket.send(jsonMsg)


    def getPlayerById(self, id):
        for player in self.players:
            if player.id == id:
                return player
        return False


    def diceSum(self):
        diceSum = 0
        for player in self.players:
            diceSum = diceSum + len(player.dice)
        return diceSum


    def validBid(self, newBid):
        try:
            newQuantity = int(newBid["quantity"])
            newValue = int(newBid["value"])
        except:
            return False
        if newQuantity >= self.diceSum() or 1 < newValue or newValue > 6:
            return False
        if newQuantity == self.prevBid["quantity"] and newValue == self.prevBid["value"]:
            return False
        if newQuantity < self.prevBid["quantity"] or newValue < self.prevBid["value"]:
            return False      
        return True


    async def handleChallenge(self, response):
        if response["id"] == self.getCurrentTurnId():
            await self.challenge()
            await self.endRound()


    def getCurrentTurnId(self):
        return self.players[self.currentTurn].id


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
            "challenge_player": self.players[self.currentTurn].name,
            "bid_player": self.players[prevIndex].name,
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


    async def endRound(self):
        for player in self.players:
            if len(player.dice) == 0:
                self.players.remove(player)
        if len(self.players) == 1:
            await self.endGame()
        else:
            await self.nextTurn() 


    async def endGame(self):
        jsonMsg = json.dumps({
            "action": "endgame",
            "winner": self.players[0].name,
            "winner_id": self.players[0].id
        })
        await asyncio.wait([ws.send(jsonMsg) for ws in userWebsockets])


#Main game loop
async def main(websocket, path):

    print('== Server Started ==')

    while True:
        response = await websocket.recv()
        response = parseMsg(response)
        print(response)

        if "action" in response:
            if response["action"] == "join":
                playerId = await playerJoin(response, websocket)
                await websocket.send(json.dumps({"action":"setup", "id": playerId}))
                if len(players) >= MIN_PLAYERS:
                    game = Game()
                    await game.nextTurn()
            elif response["action"] == "bid":
                await game.updateBid(response, websocket)
            elif response["action"] == "challenge":
                await game.handleChallenge(response)
        response = {}


async def playerJoin(response, ws):
    newId = str(uuid.uuid1())
    players.append(Player(response["name"], newId, ws))
    userWebsockets.append(ws)
    jsonMsg = {"action":"joined", "name": response["name"]}
    await asyncio.wait([ws.send(json.dumps(jsonMsg)) for ws in userWebsockets])
    return newId

#Start websocket server with asyncio
start_server = websockets.serve(main, 'localhost', 1234)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

