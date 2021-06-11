#Liar's Dice without multiplayer websockets. 
#Uses basic NPCs opponents.

import socket, sys, string, random

#Globals
MAX_PLAYERS = 3
MAX_DICE = 5
START_BID = {"quantity": 0, "value": 0}

class Player:
    def __init__(self, numDice):
        self.dice = []
        self.numDice = numDice

    def createDice(self):
        for x in range(self.numDice):
            self.dice.append(random.randint(1,6))
    
    def printDice(self):
        return " ".join(map(str, self.dice))

    def removeDie(self):
        self.dice.pop()
            

class GameClient:
    def __init__(self):
        self.players = []
        self.maxPlayers = MAX_PLAYERS
        self.maxDice = MAX_DICE
        self.user = Player(self.maxDice)
        self.currentTurn = 0 #players = 0..n-1, player = n
        self.previousBid = START_BID

    def startGame(self):
        for x in range(self.maxPlayers):
            self.players.append(Player(self.maxDice))
        self.setupRound()

    def setupRound(self):
        for player in self.players:
            player.createDice()
        self.user.createDice()
        self.currentTurn = random.randint(0,len(self.players))
        self.nextTurn()

    def nextTurn(self):
        self.printTurnStats()
        if self.currentTurn == len(self.players):
            print("It is your turn.")
            self.playerRound()
        else:
            print("It is player %s's turn" % self.currentTurn)
            self.opponentRound()

    def printTurnStats(self):
        print("======= Next Turn =========")
        print("Number of players: %s" % (len(self.players)+1))
        print("Current bid: %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))
        print("Your dice: %s" % self.user.dice)
        print("---------------------------")


    #Player Turn
    def playerRound(self):
        quantity = self.previousBid["quantity"]
        value = self.previousBid["value"]
        if quantity == 0 or value == 0:
            self.createNewBid()
        else:
            print("Previous bid: %s dice of value %s" % (quantity, value))
            userAction = self.getUserAction()
            if userAction == "B":
                self.actionBid()
            elif userAction == "C":
                self.actionChallenge()
            elif userAction == "Q":
                self.actionQuitGame()
            else:
                print("Something went wrong! Bye...")

    def createNewBid(self):
        print("What is the dice face value of the new bid?:")
        self.previousBid["value"] = self.getNumberInput(0, 6)
        maxDice = self.getDiceSum()
        print("What is the quantity of the new bid? (Total dice in game: %s)" % self.getDiceSum())
        self.previousBid["quantity"] = self.getNumberInput(0, maxDice)
        print("You have bet %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))
        self.changeTurnOrder()
        self.nextTurn()

    def getUserAction(self):
        print("Bid or Challenge? (B = Bid, C = Challenge, Q = Quit Game):")
        actionOptions = ["B", "C", "Q"]
        return self.getLetterInput(actionOptions)


    #Player Bid
    def actionBid(self):
        bidType = self.getBidType()
        if bidType == "Q":
            self.previousBid["quantity"] = self.getBidAmount()
        elif bidType == "V":
            self.previousBid["value"] = self.getBidValue()
        quantity = self.previousBid["quantity"]
        value = self.previousBid["value"]
        print("You have increased the bid. The new bid is %s dice of value %s" % (quantity, value))
        self.changeTurnOrder()
        self.nextTurn()

    def getBidType(self):
        if self.previousBid["quantity"] == self.getDiceSum():
            print("Maximum number of dice being bid, can only increase face value.")
            self.getBidValue()
        elif self.previousBid["value"] == 6:
            print("Maximum value being bid, can only increase quantity.")
            self.getBidAmount()
        else:
            print("Increase quantity or value of bid? (Q or V):")
            bidOptions = ["Q", "V"]
            return self.getLetterInput(bidOptions)

    def getBidValue(self):
        print("What is the new bid's dice face value? (Previous bid: %s):" % self.previousBid["value"])
        return self.getNumberInput(self.previousBid["value"], 6)

    def getBidAmount(self):
        print("What is the new bid's dice quantity? (Previous bid: %s):" % self.previousBid["quantity"])
        return self.getNumberInput(self.previousBid["quantity"], self.getDiceSum())

    def getLetterInput(self, letterArray):
        userInput = input('-->')
        userInput = userInput.upper()
        inList = userInput in letterArray
        while not inList:
            print('Invalid response, try again.')
            userInput = input('-->')
            userInput = userInput.upper()
            inList = userInput in letterArray
        return userInput

    def getNumberInput(self, minNumber, maxNumber = 100):
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

    def getDiceSum(self):
        sum = len(self.user.dice)
        for player in self.players:
            sum = sum + len(player.dice)
        return sum


    #Player Challenge
    def actionChallenge(self):
        print("You challenge the previous bid!")
        self.challenge()

    def challenge(self):
        if self.correctBid():
            print(self.currentTurn)
            print(len(self.players))
            if self.currentTurn == len(self.players):
                print("The bid was correct! You lose one die.")
                self.user.removeDie()
            else:
                print("The previous bid was correct! Player %s loses one die" % (self.currentTurn-1))
                self.players[self.currentTurn-1].removeDie()
        else:
            if self.currentTurn == 0:
                print("Your bid was caught! You lose one die.")
                self.user.removeDie()
            else:
                print("Player %s's bid was caught! They lose one die" % (self.currentTurn-1))
                self.players[self.currentTurn-1].removeDie()
        self.endRound()
    
    def correctBid(self):
        diceTotals = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for player in self.players:
            print("Player %s's dice: %s" % (self.players.index(player), player.dice))
            for die in player.dice:
                diceTotals[die] = diceTotals[die]+1
        
        print("bid: %s %s" % (self.previousBid["quantity"], self.previousBid["value"]))
        print("actual: %s %s" % (diceTotals[self.previousBid["value"]], self.previousBid["value"]))
        return  diceTotals[self.previousBid["value"]] >= self.previousBid["quantity"]


    #Opponent Turn
    def opponentRound(self):
        value = self.previousBid["value"]
        quantity = self.previousBid["quantity"]
        if value == 0 or quantity == 0:
            self.opponentCreateBid()
            self.changeTurnOrder()
            self.nextTurn()
        else:
            action = random.randint(0,3) #1/4th chance of opponent challenging bid
            if action == 0:
                print("Player %s is challenging the bid!" % self.currentTurn)
                self.challenge()
            else:
                print("Player %s is increasing the bid!" % self.currentTurn)
                self.opponentBid()
                self.changeTurnOrder()
                self.nextTurn()

    #Opponent Bid
    def opponentBid(self):
        rand = random.randint(0,1)
        prevValue = self.previousBid["value"]
        prevQuantity = self.previousBid["quantity"]
        if rand == 0 and prevValue < 6:
            self.previousBid["value"] = prevValue + 1
        else:
            self.previousBid["quantity"] = prevQuantity + 1
        print("The opponent has bid %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))

    def opponentCreateBid(self):
        print("Player %s is creating a new bid!" % self.currentTurn)
        self.previousBid["value"] = random.randint(1,6)
        self.previousBid["quantity"]  = random.randint(1,3)
        print("Player %s has bid: %s dice of value %s" % (self.currentTurn, self.previousBid["quantity"], self.previousBid["value"]))

    #Round End
    def endRound(self):
        print("The round has ended.")
        if len(self.user.dice) == 0:
            self.gameOver()
        else: 
            for player in self.players:
                if len(player.dice) == 0:
                    self.players.remove(player)
            if self.players == 0:
                self.wonGame()
            else:
                self.currentTurn = random.randint(0, len(self.players))
                self.previousBid = self.previousBid = {"quantity": 0, "value": 0}
                print("A new round has started.")
                self.nextTurn()

    def changeTurnOrder(self):
        if self.currentTurn == len(self.players):
            self.currentTurn = 0
        else:
            self.currentTurn = self.currentTurn + 1
    
    def gameOver(self):
        print("You have no dice! You lose the game...")
        return
    
    def wonGame(self):
        print("There are no opponents with dice left! You won the game! Congrats!")
        return

    def actionQuitGame(self):
        print("Bye~!")


game = GameClient()
game.startGame()

