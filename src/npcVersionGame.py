#Liar's Dice without multiplayer


import socket, sys, string, random

class Player:
    def __init__(self, numDice):
        self.dice = []
        self.numDice = numDice

    def createDice(self):
        for x in range(self.numDice):
            self.dice.append(random.randint(1,6))
    
    def printDice(self):
        return " ".join(map(str, self.dice))
            

class GameClient:
    def __init__(self):
        self.players = []
        self.maxPlayers = 3
        self.maxDice = 5
        self.user = Player(self.maxDice)
        self.currentTurn = 0 #players = 0..n-1, player = n
        self.previousBid = {"quantity": 0, "value": 0}

    def startGame(self):
        for x in range(self.maxPlayers):
            self.players.append(Player(self.maxDice))
        self.setupRound()

    def setupRound(self):
        #Get opponent dice
        for player in self.players:
            player.createDice()
        #Get user dice
        self.user.createDice()
        self.currentTurn = random.randint(0,len(self.players))
        self.nextTurn()

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

    def getLetterInput(self, letterArray):
        userInput = raw_input('-->')
        userInput = string.upper(userInput)
        inList = userInput in letterArray
        while not inList:
            print('Invalid response, try again.')
            userInput = raw_input('-->')
            string.upper(userInput)
            inList = userInput in letterArray
        return userInput

    #todo max number dice/value check
    def getNumberInput(self, minNumber, maxNumber = 100):
        inputNumber = raw_input('-->')
        inputNumber = int(inputNumber)
        validBid =  inputNumber > minNumber
        while not validBid:
            print("Bid not valid, try again:")
            inputNumber = raw_input('-->')
            inputNumber = int(inputNumber)
            validBid = inputNumber > minNumber
        return inputNumber

    def getUserAction(self):
        print("Bid or Challenge? (B = Bid, C = Challenge, Q = Quit Game):")
        actionOptions = ["B", "C", "Q"]
        return self.getLetterInput(actionOptions)
    
    def getBidType(self):
        print("Increase quantity or value of bid? (Q or V):")
        bidOptions = ["Q", "V"]
        return self.getLetterInput(bidOptions)

    def getBidAmount(self):
        print("What is the new bid's dice quantity? (Previous bid: %s):" % self.previousBid["quantity"])
        return self.getNumberInput(self.previousBid["quantity"])
    
    def getBidValue(self):
        print("What is the new bid's dice face value? (Previous bid: %s):" % self.previousBid["value"])
        return self.getNumberInput(self.previousBid["value"])

    def getDiceSum(self):
        sum = len(self.user.dice)
        for player in self.players:
            sum = sum + len(player.dice)
        return sum

    #If new game and bid is 0,0 allow user to make new bid
    def createNewBid(self):
        print("What is the dice face value of the new bid?:")
        self.previousBid["value"] = self.getNumberInput(1, 6)
        maxDice = self.getDiceSum()
        print("What is the quantity of the new bid? (Total dice in game: %s)" % self.getDiceSum())
        self.previousBid["quantity"] = self.getNumberInput(1, maxDice)
        print("You have bet %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))
        self.changeTurnOrder()
        self.nextTurn()
    
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

    def actionChallenge(self):
        print("Challenge Selected")
        #reveal and tally dice, see if previous bid was correct or not.
        #either challenger or person challenged loses a dice, new round starts.
        if self.wonChallenge():
            print("You won the challenge! Great job!")
            prevPlayer = self.players[self.currentTurn-1]
            print("Previous player %s will lose a die" % (self.currentTurn-1))
            prevPlayer.removeDice()
        self.endRound()
    
    def wonChallenge(self):
        #Tally up dice of all players
        diceTotals = [0,0,0,0,0,0]
        for player in self.players:
            for die in player.dice:
                diceTotals[die] = diceTotals[die]+1
        return  diceTotals[self.previousBid["value"]] == self.previousBid["quantity"]

    def changeTurnOrder(self):
        if self.currentTurn == len(self.players):
            self.currentTurn = 0
        else:
            self.currentTurn = self.currentTurn + 1

    def nextTurn(self):
        #check current turn number
        #increase current turn number until max player, then reset to 0

        print("======= Next Turn =========")
        print("Number of players: %s" % (len(self.players)+1))
        print("Current bid: %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))
        print("Your dice: %s" % self.user.dice)
        print("---------------------------")

        if self.currentTurn == len(self.players):
            print("It is your turn.")
            self.playerRound()
        else:
            print("It is player %s's turn" % self.currentTurn)
            action = random.randint(0,10) #2/3 bid or 1/3 challenge
            if action == 0:
                print("Player %s is challenging the bid!" % self.currentTurn)
                self.endRound()
            else:
                print("Player %s is increasing the bid!" % self.currentTurn)
                self.opponentBid()
                self.changeTurnOrder()
                self.nextTurn()
    
    def opponentBid(self):
        rand = random.randint(0,1)
        prevValue = self.previousBid["value"]
        prevQuantity = self.previousBid["quantity"]
        if rand == 0 and prevValue < 6:
            self.previousBid["value"] = prevValue + 1
        else:
            self.previousBid["quantity"] = prevQuantity + 1
        print("The opponent has bid %s dice of value %s" % (self.previousBid["quantity"], self.previousBid["value"]))



    #round has ended after a challenge
    #remove players without dice
    #start new currentTurn
    #reset previousBid
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
    
    def gameOver(self):
        print("You have no dice! You lose the game...")
        return
    
    def wonGame(self):
        print("There are no opponents with dice left! You won the game! Congrats!")
        return

    def actionQuitGame(self):
        print("You quit the game! Bye~!")


game = GameClient()
game.startGame()

