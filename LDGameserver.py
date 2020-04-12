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

gameMessages = {
    #Server start and lobby messages
    "server_start" : "The Lair's Dice Server has started running.\n",
    "player_joined_server" : "Player %s has joined the lobby.\n",
    "lobby_players" : "The following players are in the lobby: ",
    
    #Game countdown timer
    "timer_start" : "Enough players have joined, Lair's Dice game will begin in %s seconds.\n",
    "timer_stopped" : "The timer has been stopped. When enough players arrive timer will restart.\n",
    "timer_ended" : "The timer has ended, the game will begin shortly.\n"
    
    #Game start
    "game_start" : "A new Lair's Dice game has begun!",

    #Round start
    "player_dice" : "Player %s has the following dice: ",
    "player_turn" : "It is now player %s's turn.\n",

    #Challenge messages
    "challenge_won" : "The challenging player %s has won! Player %s was caught lying on the bid.\n",
    "challenge_lost" : "The challenging player %s has lost! Player %s had a valid bid.\n",
    
    #Bid messages
    "player_bid" : "Player %s has bid %s dice of %s value.\n",
    "invalid_bid" : "Player %s has sent an invalid bid, sending message back.\n",

    #Player quit, kicked, game endings
    "player_kicked" : "Player %s was kick from the game and sent to the lobby.\n",
    "game_end_under_min" : "The game has ended due to too few players participating.\n",
    "game_end_winner" : "The game has ended with player %s winning Lair's Dice.\n",
    
    #Error messages
    "invalid_request" : "Client has sent an invalid request. Moving on...\n"
}


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


    def removeDie():
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


    def acceptClient( self ):
        print "New client has been detected."
        newsock = self.srvsock.accept() #(host,port) pair
        self.descriptors.append( newsock )


    #Broadcast message
    def broadcast(self, message):
        for sock in self.descriptors:
            if sock != self.srvsock:
                sock.send(message)
    

    #Send message to single client
    def sendmsg(self, message, hostport):
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
        self.playerOrder = [] #Ordered list of player ids
        self.currentTurn = 0 #Id of the player who has the current turn
        self.gameStatus = "waiting"
        self.clients = {}
        self.previousBid = {"quantity": 0, "value": 0}
        self.attemptCount = MAX_ATTEMPTS
        self.countdownTimer = threading.Timer(COUNTDOWN_TIME, self.startGame)
        self.parsedMessage = ""


    #Kick player from game, send to lobby.
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
    

    #Determines how game ended and sends message about winner.
    def endGame():
        #Check if there are enough players in game
        if (len(self.playerOrder) < MIN_PLAYERS):
            printMessage["game_end_under_min"]
        #Check who has remaining dice
            print gameMessages["game_end_winner"] % (self.clients[winnerId])
        #Send message about how game ended
        endMessage = "[game_end,%s]" % (winnerId)
        self.connection.broadcast(endMessage)

        self.resetGame() #TODO Reset values and move all players to lobby


    def playerQuit(id):
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


    def playerChallenge(challegerId, bidderId):
        #Count up the user's dice quanitites and values
        diceSums = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0 }
        for key in self.clients:
            if (self.clients[key].inGame == True): #Only ingame client dice counted, maybe not needed
                dice = self.clients[key].dice
                for index in dice:
                    diceSums[dice[index]] += diceSums[dice[index]]
        
        #Check previous bid against dice sum
        if (diceSums[self.previousBid["value"]] <= self.previousBid["quantity"]):
            #Bid was correct, challenger loses dice
            print gameMessages["challenge_won"] % (challengerId, bidderId)
            self.clients["challenger_id"].dice.pop()
            challengeMessage = '[challenge_won,%s,%s]' % (challengerId, bidderId)
            self.connection.broadcast(challengeMessage)
        else:
            #Bid was incorrect, bidder loses a dice
            print gameMessages["challenge_lost"] % (challengerId, bidderId)
            self.clients["bidder_id"].dice.pop()
            challengeMessage = '[challenge_lost,%s,%s]' % (challengerId, bidderId)
            self.connection.broadcast(challengeMessage)
        #Start next round
        self.startNewRound()


    def playerBid():


    def ShowDice(self, winner, loser):
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


    #def startGame():
    # initalize servers
    # wait for new clients
    # send messages to clients of server status on join
    # start timer if enough clients
    # check if clients have left
    # game starts
    # sets player order, gives dice for players
    # handle new clients after game already started


    #originally RunGame()
    def startGame():
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


    #reset previous bid
    #get player order
    #send dice quantity messages
    #send player turn message to client
    def startNewRound():


    def manageRequests(message):
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

    


########################################################################################
#########################################################################################
#Server Class
        
class GameServer:
    def __init__( self ):
        self.port = 36712;

        self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.srvsock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.SvrState = "Waiting" #Lets server know what state the game is in

        self.ClientState = [] #Contains (ClientSocket, ClientState) tuples
        self.InGameInfoA = [] #Contains array of InGameInfo
        self.descriptors = [self.srvsock]
        self.GameWTimer = 5 #Used to time from lobby to game.
        self.PreviousBid = [0,0] #Has Dice Count and Dice Val of previous Bid (4 5's)
        self.totalclients = 0 #shows number of clients on server
        self.Order = 1 #Whos turn it is, ranking from 0 to 5, smallest to greatest player#
        self.MinPlayers = 2
        self.MaxPlayers = 5
        self.AttemptCount = 5 #Attempts currently playing player has to bid correctly
        self.AC = 5 #Stores the maximum number of player attempt counts.
        self.waitt = threading.Timer(self.GameWTimer, self.BeginGame)
        self.MaxDice = 3 #Number of dice sent at the begining of the game.

        self.ordercheck = ""


#Switches Server state to in_game. Used by the Timer in the waiting/timerwait states.
    def BeginGame(self ):
        self.PreviousBid = [0,0]
        self.SvrState = "In_Game"
        roundstart = '[round_start,%s' %(len(self.InGameInfoA))
        for x in range(0,len(self.InGameInfoA)):
            roundstart += "," + str(self.InGameInfoA[x].Order) + "," + str(self.InGameInfoA[x].DiceNo)
        roundstart += ']'
        self.broadcast(roundstart)
        self.Order = 0
        SrtPnum  = self.findranking(0)
        print 'Player ' + self.GetNumName(SrtPnum) + ' is going to go first.\n'
        self.ordercheck += str(SrtPnum)
        plturnmsg = '[player_turn,%s]' % (SrtPnum)
        for y in range(0,len(self.InGameInfoA)):  
            plrdicemsg = '[your_dice,'
            Paddress = self.InGameInfoA[y].HP
            plrdicemsg += str(self.InGameInfoA[y].DiceNo)
            for z in range(0,len(self.InGameInfoA[y].Dice)):
                plrdicemsg += "," + str(self.InGameInfoA[y].Dice[z])
            plrdicemsg += ']'
            #Send their dice, then their turn so they know what to choose
            self.sendmsg(plrdicemsg,Paddress)
        self.broadcast(plturnmsg)  

    

        
##############################################################################
#Main Server Game Loop

        
    def run( self ):
        
      print "The Lair's Dice Server has Started Running.\n"


              
      while 1:
          # Await an event on a readable socket descriptor
          (sread, swrite, sexc) = select.select( self.descriptors, [], [] )

          # Iterate through the tagged read descriptors
          for sock in sread:
              
                  
              # Received a connect to the server (listening) socket
              if sock == self.srvsock:
                  self.AcceptConnection()
                  
              else:

                # Received something on a client socket
                str1 = sock.recv(100)
                #MsgArray = self.MsgDecode(str1)


                MsgArray = self.MsgDecode2(str1)
                ##print MsgArray
                for q in range(0,len(MsgArray)):

    ##PlayerJoin
                    if (MsgArray[q][0] == "join"):
                        ##Send Status back so it knows all the users.
                        Statmsg = '[state,'
                        if self.SvrState == "Waiting":
                            Statmsg += "lobby"
                        elif self.SvrState == "TimerWait":
                            Statmsg += "lobby_with_timer"
                        else:
                            Statmsg += "in_game"
                        Statmsg += "," + str(self.totalclients) 
                        for x in range(0,len(self.ClientState)):
                            Statmsg += "," + self.ClientState[x].Pname + "," + str(self.ClientState[x].Order)
                        Statmsg += ']'
                        self.sendmsg(Statmsg,sock.getpeername())
                        ClientName = MsgArray[q][1]
                        newclientst = ClientState(sock.getpeername(), MsgArray[q][1], "lobby", self.totalclients)
                        self.ClientState.append(newclientst)
                        print 'Player %s has joined the wait room.\n' % (MsgArray[q][1])
                        msg = '[client_joined,%s,%s]' % (MsgArray[q][1], self.totalclients)
                        self.broadcast(msg)
                        self.totalclients = self.totalclients + 1
                        
                    elif (MsgArray[q][0] == "quit"):
                        self.PlayerQuit(MsgArray[q][1])
                        break
                
    ##Waiting            
                    if (self.SvrState == "Waiting"):
                #Determine if there are enough players
                        self.checkplayers()
    ##TimerWait
                    elif (self.SvrState == "TimerWait"):
                        igialen = len(self.InGameInfoA)
                        desclen = len(self.descriptors)
                        if ((igialen < self.MaxPlayers) and (desclen > igialen)):
                            self.waitt.cancel()
                            for x in range(0,len(self.InGameInfoA)):
                                self.InGameInfoA.pop()
                            print "Found player to add to upcoming game! Timer Restarting...\n"
                            self.checkplayers()
                        if (igialen < self.MinPlayers):
                            self.waitt.cancel()
                            for x in range(0,len(self.InGameInfoA)):
                                self.InGameInfoA.pop()
                            print "Not enough players for game, timer has been stopped."
                            self.SvrState = "Waiting"
    ##In_Game               
                    elif (self.SvrState == "In_Game"):
                        if len(self.InGameInfoA) == 1:
                            self.EndGame(self.InGameInfoA[0].HP)
                        #Add Timer for Attempting Here.
                            
                        for x in range(0,len(self.InGameInfoA)):
                            if sock.getpeername() == self.InGameInfoA[x].HP:
                                y = x #Identifies where the Currentplayer is in the InGameInfoA Array.
                                break
                        if (self.AttemptCount == 0):
                            self.AttemptCount = self.AC
                            self.KickPlayer(self.InGameInfoA[y].HP)
                            
    #Player Bids
                        if (MsgArray[q][0] == "bid"):
                            dcount = int(MsgArray[q][1])
                            dval = int(MsgArray[q][2])
                            pbv = self.PreviousBid[1]
                            pbn = self.PreviousBid[0]
                            print str(dval)+" "+str(dcount)+" "+str(pbv)+" "+str(pbn)
                            #bid validity: greater dice face or same face with higher ammount.
                            if (dval > pbv) or (dval == pbv and dcount > pbn): #Check if bid is valid.
                                self.AttemptCount = 5
                                print 'Player %s has bid: ' % (self.InGameInfoA[y].Pname)
                                print MsgArray[q][1] + ' dice of value ' + MsgArray[q][2] + '\n'
                                bidmsg = "[bid_report,%s,%s,%s]" % (self.InGameInfoA[y].Order,MsgArray[q][1],MsgArray[q][2])
                                self.broadcast(bidmsg)
                                if len(self.InGameInfoA)-1 > self.Order: #Increase order so person next can go.
                                    self.Order = self.Order + 1
                                else: #Go back to zero if order has gone to max.
                                    self.Order = 0
                                self.PreviousBid = [dcount, dval] 
                                self.NextTurn(self.Order)
                                
                            else: #If bid is invalid, sent a invalid_move and have them try again.
                                self.AttemptCount = self.AttemptCount - 1
                                retrymsg = "[invalid_move, %s]" % (self.AttemptCount)
                                self.sendmsg(retrymsg, sock.getpeername())
                                print 'Player %s has made an invalid bid.' % (self.InGameInfoA[y].Pname)
                                print 'They have %s tries remaining.' % (self.AttemptCount)
                                print 'current order:' + str(self.Order)
                                if self.AttemptCount == 0:
                                    self.KickPlayer(self.InGameInfoA[y].HP)
    #Player Challenges
                        elif (MsgArray[q][0] == "challenge"):
                            if self.PreviousBid == [0,0]: #Bid has not been made yet, cannot challenge.
                                self.AttemptCount = self.AttemptCount - 1
                                print 'Invalid Challenge. %s tries remaining.' % (self.AttemptCount)
                                retrymsg = '[invalid_move,%s]' % (self.AttemptCount)
                                self.sendmsg(retrymsg, sock.getpeername())
                                if self.AttemptCount == 0:
                                    self.KickPlayer(self.InGameInfoA[y].HP)
                            else:
                                self.AttemptCount = 5
                                chreportmsg = '[challenge_report, %s ]' % (self.InGameInfoA[y].Order)
                                self.broadcast(chreportmsg)
                                print 'Player has choosen to challenge!'
                                self.DetermineWinner()
                                

#Accept New Client Connection 
    def AcceptConnection( self ):
        print "New client has been detected."
        newsock, (remhost, remport) = self.srvsock.accept()
        self.descriptors.append( newsock )
        

myServer = GameServer()
myServer.run()
