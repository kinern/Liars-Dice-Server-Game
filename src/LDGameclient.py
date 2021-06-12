#Liar's Dice Client

import asyncio
import websockets
import json


messages = {
    "name" : "== Please enter your name: ",
    "connected" : 'You are connected to the Lair\'s Dice server! Hello.',
    "playerJoined" : 'Player %s has joined.',
    "newGameStart" : (
        "------------------------------------------------"
        "            Let's Play Lair's Dice!             "
        "------------------------------------------------"
    ),
    "roundStart" : (
        "=========== Next Turn ============="
        "Players: %s" 
        "Current bid: %s dice of value %s" 
        "Your dice: %s"
        "It is now player %s\'s turn."
        ),
    "yourTurnBidOnly" : "You are the starting player! You will need to bid.",
    "yourBidQuantity" : "== How many dice will you bid? (previous bid: %s dice of value %s):",
    "yourBidValue" : "== What value of dice will you bid? (previous bid: %s dice of value %s):",
    "yourAction" : '== It is your turn! Will you bid or challenge? ("B" or "C"):',
    
    "playerBid" : "Player %s has increased the bid to %s dice of value %s.",
    "challengeLostResult" : (
        "Player %s has challenged the bid!"
        "The bid of %s dice of value %s was correct."
        "Player %s has lost the challenge and loses one die."
        "+++++++++++ Round Ended ++++++++++++"
    ),
    "challengeWonResult" : (
        "Player %s has challenge the bid!"
        "The bid of %s dice of value %s was incorrect"
        "Player %s has lost the challenge and loses one die."
        "+++++++++++ Round Ended ++++++++++++"
    ),
    "playerLost" : "Player %s has no more dice and has been removed from play.",
    "endGame" : "The game has ended, player %s is the winner!",
    "endGameWon" : "The game has ended, you have won the game! Congrats!"
}


def parseMsg(msg):
    jsonArr = json.loads(msg)
    return jsonArr


class Player:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.dice = []


player = Player()


#Send username to the game server
async def gameLoop():
    async with websockets.connect('ws://localhost:1234') as socket:

        print('== Client Started ==')

        #Initial setup: send name to server
        if player.id == 0:
            playerName = input(messages.name)
            jsonMsg = {
                "name": playerName
            }
            await socket.send(jsonMsg)
        
        #Get server message
        response = await socket.recv()
        response = parseMsg(response)
        print(response)

        #Handle message
        if response.has_key("action"):
            if response["action"] == "setup":
                playerId = response["id"]
                #Get id from server
                print(messages["connected"])
            if response["action"] == "joined":
                #Print player has joined message
                print(messages["joined"], response["name"])
            if response["action"] == "start":
                #Print game has started message
                print(messages["newGameStart"])
            if response["action"] == "next_turn":
                handleNextTurn(response)
            if response["action"] == "bid":
                #Print bid message
                print(messages["playerBid"])
            if response["action"] == "challenge":
                handleChallenge(response)
            if response["action"] == "end_game":
                handleEndgame(response)
        #Empty response
        response = {}


async def handleNextTurn(response):
    #Find name of current turn player by searching through players by turn_id
    #Print next turn information
    print(messages["roundStart"], response["players"], response["prev_bid"], response["dice"], response["turn_name"])
    #If turn id is player id, get player's move
    if response["turn_id"] == playerId:
        if response["prev_bid"]["val"] == 0:
            print(messages["yourTurnBidOnly"])
            bidQuantity = input(messages["yourBidQuantity"])
            bidValue = input(messages["yourBidValue"])
        else:
            actionType = input(messages["yourAction"])
            if actionType == "B":
                bidQuantity = input(messages["yourBidQuantity"])
                bidValue = input(messages["yourBidValue"])
            elif actionType == "C":
                #Send challenge message to server...
                await socket.send("{action:'challenge', gameId:gameId, id:playerId}")


def handleChallenge(response):
    #Print challenge/round end message
    if (response["won"] == 1):
        print(messages["challengeWonResult"])
    else:
        print(messages["challengeLostResult"])


def handleEndgame(response):
    #Check if winner id is players's id
    #Print end game message
    if (response["winner_id"] == playerId):
        print(messages["endGameWon"])
    else:
        print(messages["endGame"])


asyncio.get_event_loop().run_until_complete(gameLoop())
