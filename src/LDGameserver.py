# Liar's Dice Server
# 
#
# Receives clients and sets up game. 
# When minimum players have connected, has countdown to game start
# If other players arrive after game has started, they can watch the messages out of game.
# Deals dice to players and gives order of each player.
# Receieves player's actions and sends results to all players.
# 
# 

import gameMessages
import socket, select, string, threading, random, sys


####################################################################################
# Globals and configs

PORT = 36712
MIN_PLAYERS = 2
MAX_PLAYERS = 5
COUNTDOWN_TIME = 5
MAX_ATTEMPTS = 5
MAX_DICE = 5


####################################################################################
# Messages


####################################################################################
# Connection related functionality

class ClientConnection:
    def __init__(self, host, port)
        self.host = host
        self.port = port


###################################################################################
# Client sends name of player

class ClientPlayer: #originally InGameInfo
    def __init__(self, host, port, name):
        self.connection = ClientConnection(host, port)
        self.name = name
        self.id = id
        self.inGame = False #Player is either part of game or watching game
        self.dice = []


    def removeDie(self):
        self.die.pop()


    #Roll new dice
    def rollDice(self):
        diceLen = len(self.dice)
        self.dice = []
        for x in range(0,diceLen):
            y = random.randint(1,6)
            self.dice.append(y)

#################################################################################
# Sends and recieves messages from the Clients

class Connection:
    def __init__(self, port):
        self.port = port;
        self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.srvsock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.descriptors = [self.srvsock] #TODO ???


    def acceptClient(self):
        print "New client has been detected."
        newsock = self.srvsock.accept() #(host,port) pair
        self.descriptors.append( newsock )


    #Broadcast message
    def broadcast(self, message):
        for sock in self.descriptors:
            if sock != self.srvsock:
                sock.send(message)
    

    #Send message to single client
    def sendMessage(self, message, hostport):
        for sock in self.descriptors:
            if sock.getpeername() == hostport:
                sock.send(mstring)
                break


    #Parses received client message into arrays
    def parseMessage(self,pstring): #originally MsgDecode2()
        StrBuild = ""
        ArrayBuild = []
        DecodedArray = []
        for y in range(0,len(pstring)):
                if pstring[y] == ',':
                        ArrayBuild.append(StrBuild)
                        StrBuild = ""
                elif pstring[y] == ']':
                        ArrayBuild.append(StrBuild)
                        DecodedArray.append(ArrayBuild)
                        StrBuild = ""
                        ArrayBuild = []
                else:
                    if pstring[y] != '[':
                        StrBuild += pstring[y]
                
        return DecodedArray



####################################################################################   
# GameServer Class

####################
# self.gameStatus string:
# "waiting" - waiting for minimum ammount of players to arrive.
# "countdown" - enough players have arrived, server is counting down until game starts.
# "in_game" - game is being played

####################
# self.clients dictionary:
# { player_id : ClientPlayer(player_id,..), player_id2 : ClientPlayer(player_id2,..) }
# Since player names/info is looked up by ids passed by the client
# searching by id should be easier using the dictionary.

class GameServer:
    def __init__(self)
        self.connection = Connection()
        self.clients = {}
        self.gameStatus = "waiting"
        self.countdownTimer = threading.Timer(COUNTDOWN_TIME, self.startGame)
        self.playerOrder = [] #Ordered list of player ids
        self.currentTurn = 0 #Id of the player who has the current turn
        self.previousBid = {"quantity": 0, "value": 0}
        self.attemptCount = MAX_ATTEMPTS
        self.parsedMessage = ""

    #def startGame():
    # initalize servers
    # wait for new clients
    # send messages to clients of server status on join
    # start timer if enough clients
    # check if clients have left
    # game starts
    # sets player order, gives dice for players
    # handle new clients after game already started

    def startLobby(self):
        print gameMessages["sever_start"]
        wait 1:
            #Wait for client requests
            (sread, swrite, sexc) = select.select( self.descriptors, [], [] )
            for sock in sread:

                # Received a connect to the server (listening) socket
                if sock == self.srvsock:
                  self.connection.acceptClient()  
                else:
                    message = sock.recv(100)
                    if (message != ''):
                        message = self.connection.parseMessage(message)
                        self.manageRequest(message)
            #check number of players
            #if enough players and no timer, then start timer.
            #at the end of timer, check player and 
            #check the countdown timer
            #start the game if enough players and timer ended
            #reset and stop timer if too few players
            #start timer if enough players has joined and timer is off

    #Check if enough players to start game
    def countdownEnded(self):

    def startGame(self):

    #reset previous bid
    #get player order
    #send dice quantity messages
    #send player turn message to client
    def startNewRound(self):


    def playerChallenge(self, challegerId, bidderId):
        
        #Get sum of all dices
        diceSums = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0 }
        for key in self.clients:
            if (self.clients[key].inGame == True): #Only ingame client dice counted, maybe not needed
                dice = self.clients[key].dice
                for index in dice:
                    diceSums[dice[index]] += diceSums[dice[index]]
        
        #Check previous bid
        if (diceSums[self.previousBid["value"]] <= self.previousBid["quantity"]):
            #Challenge won
            print gameMessages["challenge_won"] % (challengerId, bidderId)
            self.clients["challenger_id"].dice.pop()
            challengeMessage = '[challenge_won,%s,%s]' % (challengerId, bidderId)
            self.connection.broadcast(challengeMessage)
        else:
            #Challenge lost
            print gameMessages["challenge_lost"] % (challengerId, bidderId)
            self.clients["bidder_id"].dice.pop()
            challengeMessage = '[challenge_lost,%s,%s]' % (challengerId, bidderId)
            self.connection.broadcast(challengeMessage)
        
        #Start next round
        self.startNewRound()


    def playerBid(self, quantity, value):
        #Check against previous bid and dice pool
        if (self.previousBid["quantity"] <= quantity) and (self.previousBid["value"] <= value):
            self.attemptCount = self.attemptCount-1
            if (self.attemptCount < 1):
                self.kickPlayer(self.currentTurn)
            else:
                invalidMessage = '[invalid_move,%s]' % self.attemptCount
                this.connection.sendMessage(invalidMessage)
        else:
            #Update previous bid
            #Send all users new bid
            bidMessage = '[bid_updated,%s,%s,%s]' % (self.currentTurn, quantity, value)
            self.connection.broadcast(bidMessage)
        self.nextPlayerTurn()

    #Change order and send message to next player
    def nextPlayerTurn(self):
        orderIndex = self.playerOrder.index(self.currentTurn)
        orderIndex = orderIndex + 1
        if (orderIndex > len(self.playerOrder)):
            orderIndex = 0
        self.currentTurn = self.playerOrder[orderIndex]
        turnMessage = '[player_turn,%s]' % (self.currentTurn)
        self.connection.broadcast(turnMessage)


    def showDice(self, winner, loser):
        roundendmsg = '[round_end,%s' % (loser)
        for x in range(0,len(self.InGameInfoA)):
            roundendmsg += "," + str(self.InGameInfoA[x].Order) +","+ str(self.InGameInfoA[x].DiceNo)
            for y in range(0,len(self.InGameInfoA[x].Dice)):
                roundendmsg += "," + str(self.InGameInfoA[x].Dice[y])
        roundendmsg += ']'
        self.broadcast(roundendmsg)
        ##New Dice Generated here##
        for x in range(0,len(self.InGameInfoA)):
            self.InGameInfoA[x].Dice = self.DiceGen(self.InGameInfoA[x].DiceNo)
        for x in range(0,len(self.InGameInfoA)):
            if loser == self.InGameInfoA[x].Order:
                if (len(self.InGameInfoA[x].Dice) > 0):
                    self.InGameInfoA[x].Dice.pop()
                    self.InGameInfoA[x].DiceNo = self.InGameInfoA[x].DiceNo - 1
                if self.InGameInfoA[x].DiceNo == 0:
                    self.KickPlayer(self.InGameInfoA[x].HP)
                    break




    def manageRequests(self, message):
        if (message  == 'join'):
            self.playerJoined(challenger_id,bidder_id)
        elif (message == 'quit'):
            self.playerQuit(id)
        elif (message == 'bid'):
            self.playerBid(challenger_id,bidder_id)
        elif (message == 'challenge'):
            self.playerChallenge(challenger_id,bidder_id)
        else:
            print gameMessages["invalid_request"]
    

    def kickPlayer(self, id):

        #Send player kicked message to everyone.
        print gameMessages["player_kicked"] % (self.clients[id].name)
        kickMessage = '[client_kicked,%s]' % (id)
        self.connection.broadcast(kickMessage) 
        
        #Update order, player dice and attempt count
        self.attemptCount = MAX_ATTEMPTS
        self.playerOrder.remove(id)
        self.clients[id].dice = []
        self.clients[id].inGame = False

        #End game if too few players or start next round
        if (len(self.playerOrder) < MIN_PLAYERS):
            self.endGame() #TODO End with not enough players (this needs param to indicate why game ended...)
        else:
            self.nextTurn(self.Order)


    def playerQuit(self, id):

        #Send messages to self and players.
        printMessage["player_quit"] % (self.clients[id].name)
        quitMessage = '[player_quit,%s]' % (id)
        self.connection.broadcast(quitMessage)

        #Reset values
        self.client[id].inGame = False
        self.client[id].dice = []
        self.playerOrder.remove(id)

        #End game if not enough players
        if (len(self.playerOrder) < MIN_PLAYERS):
            self.endGame()

        #Start a new round
        self.startNewRound() #TODO


    def endGame(self):

        #Check if there are enough players in game
        if (len(self.playerOrder) < MIN_PLAYERS):
            printMessage["game_end_under_min"]
        #Check who has remaining dice
            print gameMessages["game_end_winner"] % (self.clients[winnerId])
        #Send message about how game ended
        endMessage = "[game_end,%s]" % (winnerId)
        self.connection.broadcast(endMessage)
        self.resetGame() #TODO Reset values and move all players to lobby

    

####################################################################################################

gameServer = GameServer()
gameServer.startLobby()
