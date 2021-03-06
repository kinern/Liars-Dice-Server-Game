import asyncio
import websockets
import uuid
import json
import random

#Liar's Dice Server

#Globals
MAX_DICE = 2
MIN_PLAYERS = 2

##
#   Message Action Keywords
#
#   setup - gives new client their player id
#   joined - broadcasts that new client has joined
#   next_turn - broadcasts game information and current turn
#   bid - broadcasts clients bid information
#   invalid_bid - sends user message that bid sent was invalid
#   challenge - broadcasts challenge result
#   endgame - broadcasts the winner of game
#   
##


class Player:
    def __init__(self, name, id, ws):
        self.name = name
        self.id = id
        self.websocket = ws
        self.numDice = MAX_DICE
        self.dice = self.createDice()
    

    def createDice(self):
        dice = []
        for x in range(self.numDice):
            dice.append(random.randint(1,6))
        return dice
    

def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


class Game:
    def __init__(self):
        #Game variables
        self.id = "" 
        self.currentTurn = 0
        self.prevBid = {"quantity": 0, "value":0}
        
        #Array of in game Player objects
        self.players = []
        
        #Store websockets so players out of game can recieve broadcasts
        # [{player_id, websocket},..]
        self.connections = []


    def getPlayerNames(self):
        names = []
        for player in self.players:
            names.append(player.name)
        return names


    def getPlayerById(self, id):
        for player in self.players:
            if player.id == id:
                return player
        return False


    def getCurrentTurnId(self):
        return self.players[self.currentTurn].id


    def getCurrentTurnName(self):
        return self.players[self.currentTurn].name


    #Returns total sum of dice from all players
    def diceSum(self):
        diceSum = 0
        for player in self.players:
            diceSum = diceSum + len(player.dice)
        return diceSum


    #Returns object with sums of each value of all of players dice
    def getDiceTotals(self):
        diceTotals = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for player in self.players:
            for die in player.dice:
                diceTotals[die] = diceTotals[die]+1
        return diceTotals

    async def nextTurn(self):

        self.currentTurn = 0 if self.currentTurn >= (len(self.players)-1) else self.currentTurn + 1
        playerNames = self.getPlayerNames()
        currentName = self.getCurrentTurnName()
        currentId = self.getCurrentTurnId()

        for player in self.players:
            jsonMsg = json.dumps({
                    "action": "next_turn", 
                    "players": playerNames, 
                    "prev_bid": self.prevBid,
                    "dice": player.dice,
                    "turn_id": currentId, 
                    "turn_name": currentName
                    })
            await player.websocket.send(jsonMsg)
        
        print("== Next Round ==")
        print("Players: %s" % playerNames)
        print("Prev Bid: %s dice of value %s" % (self.prevBid["quantity"], self.prevBid["value"]))
        print("Current turn: %s" % self.getCurrentTurnName())        
        print("\n")


    #Bidding
    async def updateBid(self, response):
        playerName = self.getPlayerById(response["id"]).name
        playerSocket = self.getPlayerById(response["id"]).websocket
        if response["id"] == self.getCurrentTurnId():
            if self.validBid(response["new_bid"]):
                self.prevBid["quantity"] = response["new_bid"]["quantity"]
                self.prevBid["value"] = response["new_bid"]["value"]
                jsonMsg = json.dumps({
                    "action":"bid",
                    "player": playerName,
                    "new_bid" : response["new_bid"]
                })
                for player in self.players:
                    await player.websocket.send(jsonMsg)
                print("Player %s bids %s dice of value %s." % (playerName, response["new_bid"]["quantity"], response["new_bid"]["value"]))
                await self.nextTurn()
            else:
                #resend request to bidder
                jsonMsg = json.dumps({
                    "action": "bid_invalid",
                    "id": response["id"],
                    "prev_bid": self.prevBid
                })
                await playerSocket.send(jsonMsg)
                print("Player %s sent invalid bid." % playerName)
        else:
            print("Player %s sent bid while not their turn." % playerName)


    def validBid(self, newBid):
        try:
            newQuantity = int(newBid["quantity"])
            newValue = int(newBid["value"])
        except:
            print("New bid int casting failed")
            return False
        if newQuantity >= self.diceSum() or newValue < 1 or newValue > 6:
            print("Bid value not in range 1 to 6 or quantity more than sum of all dice")
            return False
        if newQuantity == int(self.prevBid["quantity"]) and newValue == int(self.prevBid["value"]):
            print("Same bid as previous")
            return False
        if newQuantity < int(self.prevBid["quantity"]) or newValue < int(self.prevBid["value"]):
            print("New bid lower than previous bid")
            return False      
        return True


    #Challenging
    async def handleChallenge(self, response):
        if response["id"] == self.getCurrentTurnId():
            await self.challenge()
            await self.endRound()
        else:
            print("Player %s tried challenge but it's not their turn." % self.getPlayerById[response["id"]].name)


    async def challenge(self):
        playerLen = len(self.players)
        prevIndex =  (playerLen - 1) if self.currentTurn <= 0 else (self.currentTurn - 1)
        currName = self.players[self.currentTurn].name
        prevName = self.players[prevIndex].name
        challengeResult = self.correctBid()
        if challengeResult:
            #Challenge won, previous player loses dice
            print("Player %s challenged %s's bid and and won! Player %s loses 1 die." % (currName, prevName, prevName))
            self.players[prevIndex].numDice -= 1
        else:
            #Challenge lost, current player loses dice
            print("Player %s challenged %s's bid and and lost! Player %s loses 1 die." % (currName, prevName, currName))
            self.players[self.currentTurn].numDice -= 1
        jsonMsg = json.dumps({
            "action":"challenge",
            "challenge_name": currName,
            "bid_name": prevName,
            "prev_bid" : self.prevBid,
            "result": challengeResult,
            "result_dice": self.getDiceTotals()
        })
        for player in self.players:
            await player.websocket.send(jsonMsg)


    def correctBid(self):
        diceTotals = self.getDiceTotals()
        return  diceTotals[int(self.prevBid["value"])] >= int(self.prevBid["quantity"])


    async def endRound(self):
        print("The round has ended.")
        for player in self.players:
            print("Player %s's dice: %s" % (player.name, player.dice))
            player.dice = player.createDice()
            if len(player.dice) == 0:
                jsonMsg = {
                    "action": "lostgame"
                }
                await player.websocket.send(json.dumps(jsonMsg))
                self.players.remove(player)
        print("\n")
        if len(self.players) == 1:
            await self.endGame()
        else:
            self.prevBid = {"quantity":0, "value":0}
            await self.nextTurn() 


    async def endGame(self):
        jsonMsg = json.dumps({
            "action": "endgame",
            "winner": self.players[0].name,
            "winner_id": self.players[0].id
        })
        print("The game has ended, the winner is %s!" % self.players[0].name)
        for player in self.players:
            await player.websocket.send(jsonMsg)

game = Game()

#Players in lobby waiting for enough players to start a game
lobbyPlayers = []

#Players waiting before the game starts
waitingPlayers = []



#Main game loop
async def main(websocket, path):

    #Todo: lobby with array of games instead of single game instance
    games = []

    print('== Server Started ==')
    while True:
        
        response = await websocket.recv()
        response = parseMsg(response)

        if "action" in response:
            if response["action"] == "join":
                await playerJoin(response, websocket)
                if len(game.players) >= MIN_PLAYERS:
                    # newGame = Game()
                    # for player in lobbyPlayers:
                    #     newGame.players.append(player)
                    #     waitingPlayers.append(player)
                    #     lobbyPlayers.remove(player)
                    # await newGame.nextTurn()
                    await game.nextTurn()
            elif response["action"] == "bid":
                await game.updateBid(response)
            elif response["action"] == "challenge":
                await game.handleChallenge(response)
        response = {}


async def playerJoin(response, ws):
    id = str(uuid.uuid1())
    game.players.append(Player(response["name"], id, ws))
    await ws.send(json.dumps({"action":"setup", "id": id}))
    jsonMsg = {"action":"joined", "name": response["name"]}
    for player in game.players:
        await player.websocket.send(json.dumps(jsonMsg))


#Start websocket server with asyncio
start_server = websockets.serve(main, 'localhost', 1234)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

