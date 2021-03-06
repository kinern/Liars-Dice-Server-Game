#Liar's Dice Client

import asyncio
import websockets
import json


messages = {
    "name" : "== Please enter your name: ",
    "connected" : 'You are connected to the Lair\'s Dice server! Hello.',
    "joined" : 'Player %s has joined.',
    "newGameStart" : (
        "------------------------------------------------\n"
        "            Let's Play Lair's Dice!             \n"
        "------------------------------------------------\n"
    ),
    "roundStart" : (
        "=========== Next Turn =============\n"
        "Players: %s\n" 
        "Current bid: %s dice of value %s\n" 
        "Your dice: %s\n"
        "It is now player %s\'s turn.\n"
        ),
    "yourTurnBidOnly" : "You are the starting player! You can only bid.",
    "yourBidQuantity" : "How many dice to bid? (previous: %s dice of value %s):",
    "yourBidValue" : "What dice face value to bid? (previous: %s dice of value %s):",
    "yourAction" : 'Your turn! Bid or challenge? ("B" or "C"):',
    "playerBid" : "Player %s increased the bid to %s dice of value %s.",
    "challengeLostResult" : (
        "Player %s challenged the bid!\n"
        "The bid of %s dice of value %s was correct.\n"
        "Player %s lost the challenge and loses one die.\n"
        "+++++++++++ Round Ended ++++++++++++\n"
    ),
    "challengeWonResult" : (
        "Player %s challenged the bid!\n"
        "The bid of %s dice of value %s was incorrect\n"
        "Player %s lost the challenge and loses one die.\n"
        "+++++++++++ Round Ended ++++++++++++\n"
    ),
    "playerLost" : "Player %s has no dice and was removed.",
    "endGame" : "The game ended, player %s is the winner!",
    "endGameWon" : "You won the game! Congrats!",
    "bidInvalid" : "The bid was invalid, try again.",
    "lostGame" : "You have run out of dice and are out of the game!"
}


def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


class Player:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.dice = []


class Game:
    def __init__(self, player):
        self.serverSocket = None
        self.response = None
        self.player = player

    # Next Turn
    async def nextTurn(self):
        print(messages["roundStart"] % (
            self.response["players"], 
            self.response["prev_bid"]["quantity"], 
            self.response["prev_bid"]["value"], 
            self.response["dice"], 
            self.response["turn_name"])
        )
        if self.response["turn_id"] != self.player.id:
            return
        if self.response["prev_bid"]["value"] == 0:
            await self.newBid()
        else:
            print(messages["yourAction"])
            actionType = inputHelper.getLetterInput(["B", "C"])
            if actionType == "B":
                await self.updateBid()
            elif actionType == "C":
                await self.challenge()

    async def handleInvalidBid(self):
        print(messages["bidInvalid"])
        await self.bid()

    ## Bidding
    async def bid(self):
        if self.response["prev_bid"]["value"] == 0:
            await self.newBid()
        else:
            await self.updateBid()

    async def newBid(self):
        print(messages["yourTurnBidOnly"])
        await self.updateBid()

    async def updateBid(self):
        yourBidQuantity = messages["yourBidQuantity"] % (
            self.response["prev_bid"]["quantity"], 
            self.response["prev_bid"]["value"]
        )
        yourBidValue = messages["yourBidValue"] % (
            self.response["prev_bid"]["quantity"], 
            self.response["prev_bid"]["value"]
        )
        print(yourBidQuantity)
        bidQuantity = input("-->")
        print(yourBidValue)
        bidValue = input("-->")
        jsonMsg = {
            "action": "bid",
            "id": self.player.id,
            "new_bid": {"quantity": bidQuantity, "value": bidValue}
        }
        await self.serverSocket.send(json.dumps(jsonMsg))
    
    ## Challenging
    async def challenge(self):
        jsonMsg = {
            "action":"challenge",
            "id": self.player.id
        }
        await self.serverSocket.send(json.dumps(jsonMsg))

    def handleChallenge(self):
        print(self.response["result"])
        msg = messages["challengeWonResult"] if self.response["result"] == 1 else messages["challengeLostResult"]
        fullMsg = (msg % (
            self.response["challenge_name"], 
            self.response["prev_bid"]["quantity"], 
            self.response["prev_bid"]["value"], 
            self.response["bid_name"])
        )
        print(fullMsg)

    ## End Game
    def endgame(self):
        msg = messages["endGameWon"] if self.response["winner_id"] == self.player.id else messages["endGame"]
        print(msg)
    
    def lostgame(self):
        print(messages["lostGame"])



class InputHelper:

    def enterName(self):
        print(messages["name"])
        name = input('-->')
        name = name.strip()
        while len(name) < 1:
            name = input('-->')
            name = name.strip()
        return name

    def getLetterInput(self, letterArray):
        userInput = input('-->')
        userInput = userInput.strip().upper()
        inList = userInput in letterArray
        while not inList:
            print('Invalid response, try again.')
            userInput = input('-->')
            userInput = userInput.strip().upper()
            inList = userInput in letterArray
        return userInput

    def getNumberInput(self, minNumber = 0, maxNumber = 100):
        inputNumber = input('-->')
        if inputNumber.isdigit():
            inputNumber = int(inputNumber)
        validBid =  inputNumber > minNumber and inputNumber <= maxNumber
        while not validBid:
            print("Bid not valid, try again:")
            inputNumber = input('-->')
            if inputNumber.isdigit():
                inputNumber = int(inputNumber)
            validBid = inputNumber > minNumber and inputNumber <= maxNumber
        return inputNumber

inputHelper = InputHelper()

#Send username to the game server
async def gameLoop():
    async with websockets.connect('ws://localhost:1234') as socket:

        player = Player()
        game = Game(player)

        print('== Client Started ==')
        game.serverSocket = socket
        prevMsg = {"action": ""}

        #Initial setup: send name to server
        if game.player.id == 0:
            game.player.name = inputHelper.enterName()
            jsonMsg = {
                "action":"join",
                "name": game.player.name
            }
            await socket.send(json.dumps(jsonMsg))
        
        #Get server message
        while True:
            response = await socket.recv()
            response = parseMsg(response)
            game.response = response

            #Handle message
            #Todo handle multiple invalid bids
            if "action" in response and response["action"] != prevMsg["action"]:
                prevMsg = response
                # Player Info Message
                if response["action"] == "setup":
                    game.player.id = response["id"]
                    print(messages["connected"])
                
                # Server Broadcasted Messages
                if response["action"] == "joined":
                    print(messages["joined"] % (response["name"]))
                if response["action"] == "start":
                    print(messages["newGameStart"])
                if response["action"] == "bid":
                    print(messages["playerBid"] % (response["player"], response["new_bid"]["quantity"], response["new_bid"]["value"]))
                
                # Game Messages
                if response["action"] == "next_turn":
                    await game.nextTurn()
                if response["action"] == "bid_invalid":
                    if response["id"] == game.player.id:
                        await game.handleInvalidBid()
                if response["action"] == "challenge":
                    game.handleChallenge()
                if response["action"] == "endgame":
                    game.endgame()
                if response["action"] == "lostgame":
                    game.lostgame()
                
            #Empty response
            response = {}


asyncio.get_event_loop().run_until_complete(gameLoop())
asyncio.get_event_loop().run_forever()
