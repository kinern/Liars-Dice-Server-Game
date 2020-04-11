##############################################################################
#Liar's Dice Client

#Messages sent by client
# Player Joins - "player_join", player_name, player_message 
# Player Bids - "player_bid", player_id, value, quantity
# Player Challenges "player_challenge", from_id, to_id
# Player Quits - "player_quit", player_id

#Messages received by the client
# Game Status - "game_status", "status_id"
# Game Start - "game_start"
# Get Dice - "get_dice", dice_value 1..n
# Bid Made - "bid", player_name, message
# Challenge Made - "challenge", message
# Player Kicked - "player_kicked", message
# Game Ended - "game_ended", message

import socket, sys, string, random



##############################################################################
#Global Variables / Configs
host = 'localhost' #Host for connecting to server.
port = 36712 #Port for connecting to server
autoMode = false #Generates username and moves automatically.
timeoutSeconds = 300 #Number of seconds until server timeout has triggered.



#############################################################################
# Game Messages

gameMessages = {

    "joined_lobby": "%s has joined the lobby.\n",
    "your_dice": "You currently have %s dice: %s",
    "order_number": "Your order number is %s.\n",
    "player_turn" : "It is now %s turn.\n",
    "player_bid" : "Player bid %s dice of value %s.\n",
    "you_bid" : "You have bid %s dice of value %s\n.",
    "you_challenge": "You have challenged %s's bid!\n"
    "challenge": "%s has challenged %s!\n",
    "challenge_after": "Aftermath of challenge: \n%s has lost the round and a die.\nThe following dice ammount for each player was: ",
    "user_turn": "It is your turn! Bid or Challenge? ('B' or 'C')\n",
    "invalid_action" : "The action is invalid, please try again.",
    "turn_change": "It is now %s turn.\n",
    "previous_bid": "The previous player bid %s dice with %s value.\n",
    "bid_quantity": "How many dice will you bid?\n",
    "bid_value": "What value of dice will you bid?\n",
    "invalid_bid": "The bid %s dice of %s value does not work with the previous bid of %s dice of %s value. Please try again.\n",
    "player_quit": "Player %s has quit the game\n",
    "player_kicked": "Player %s has been kicked out of the game!\n",
    "connecting" : "Connecting to server...\n",
    "connection_timeout": "Server took too long to respond. That's a shame.\n",
    "connected" : "You have connected to the server.\n",
    "you_joined_lobby": "You have joined the lobby.\n",
    "you_quit": "Thank you for playing!\n",
    "you_kicked" : "You have been kicked out of the game! Better luck next time!\n",
    "enter_name": "Please enter your name (1-10 characters): ",
    "end_thanks" : "Thank you for playing Liar's Dice!\n",
    "invalid_received" : "Invalid message has been received from the server. Moving on...\n"
    "lobby_status": 'Currently the server is waiting for more clients.',
    "lobby_timer_status" :'Currently the server has enough clients and waiting for the game to begin.',
    "in_game_status" : 'Currently there is a game already running on the server.',
    "names_list" : 'Players on the server: %s',
    "timer_start" : "A new Lair's Dice game will begin in %s seconds.",
    "round_begin" : 'The round has begun with %s players.',
    "total_dice" : "The total number of dice among players is %s",
    "reset_bid" : "The bid on dice has been reset to 0."
}



##############################################################################
#Connection Class
#Connects to the server, receives and sends messages.
class Connection:
    def __init__( self, host, port):
        self.port = port;
        self.host = host;
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.settimeout(timeoutSeconds)
        self.State = "Connect" 

    def sendMessage(message):
        self.clientsocket.send(message)

    def connectToServer():
        self.clientsocket.connect(self.host, self.port)

    #Polls for message
    def getMessage():
        #recv() is a blocking call so it will pause until it receives data.
        message = self.clientsocket.recv(1024)
        return self.parseMessage(message)

    #MessageDecode 
    #[Messages will be like this, so maybe just explode function with ','?]
    def parseMessage(message):
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



##########################################################################
#Player Class
#Keeps track of player name, id and dice
class Player:
    def __init__(self):
        self.name = "" 
        self.id = 0
        self.dice = []
        self.maxNameLength = 10
        self.currentBid = {"quantity" : 0, "value" : 0}

    #Creates random 10 letter name
    def randomName(nameLength):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(nameLength))

    def getDiceString(){
        diceString = ', '.join(self.dice)
        return diceString
    }

    #Get name from input
    def getName():
        while 1:
            print gameMessages["enter_name"]
            if autoMode == True:
                inputName = self.randomName(maxNameLength)
            else:
                inputName = raw_input('-->')
            #Check if quitting or name is incorrect length 
            nameLength = len(inputName);
            if string.upper(inputName) == "QUIT":
                return False
            elif (nameLength > 10) or (nameLength == 0):
                print 'Number of letters entered out of range. Try again.'
            else:
                break
        self.name = inputName
        return True
    
    #Get quantity bid from input
    def getBidQuantity():
        while 1:
            print gameMessages["bid_quantity"]
            inputQuantity = raw_input('-->')
            inputQuantity = sting.upper(inputQuantity)
            if (inputQuantity == "QUIT") or (inputQuantity == "Q"):
                return False
                break
            else if (inputQuantity < previousBid["quantity"]):
                print gameMessages["invalid_bid"]
            else:
                break
        self.currentBid["quantity"] : inputQuantity
        return True
    
    #Get value bid from input
    def getBidValue():
        while 1:
            print gameMessages["bid_value"]
            inputValue = raw_input('-->')
            inputValue = sting.upper(inputQuantity)
            if (inputValue == "QUIT") or (inputValue == "Q"):
                return False
                break
            else if (inputQuantity < previousBid["quantity"]):
                print gameMessages["invalid_bid"]
            else if ():
                print gameMessages["invalid_bid"]
            else if ():
                print gameMessages["invalid_bid"]
            else:
                break
        self.player.currentBid["quantity"] : inputQuantity
        return True


#############################################################################
# Opponent Class

#todo: (Maybe don't send opponent ids to clients...?)
class Opponent:
    def __init__(self, name, id):
        self.name
        self.id


#############################################################################
#GameClient Class
#Main Game Functionality
class GameClient:
    def __init__(self, host, port):
        self.connection = self.Connection(host,port)
        self.player = self.Player()
        self.previousBid =  {"quantity": 0, "value": 0}
        self.previousPlayerName = ""
        self.opponents = []
        self.parsedMessage = []
        self.totalDice = 0
        #Keep track of opponent's added


    #TODO
    def getTotalDiceQuantity():
        return 10


    #Change the global autoplay setting
    def setAuto():
        print 'Would you like to turn Auto-play on? (Y/N): '
        autostr = raw_input('-->')
        autostr = string.upper(autostr)
        if (autostr == 'Y') or (autostr == 'YES'):
            autoMode = True
            print 'Auto-play has been turned on.\n'
        else:
            print 'Auto-play is off.\n'


    #Game intialization
    def joinGame():
        #Connect to game server
        print gameMessages['connecting']
        connected = self.connection.connectToServer()
        if (!connected):
            print gameMessages['connection_timeout']
            return
        print gameMessages['connected']
        #Get player name from user input.
        self.player.getName()
        #Send join request with player name to server.
        joinRequest = '[join_game,%s]' % (self.player.name)
        self.clientsocket.send(joinRequest)
        #Go to main game loop and wait for server messages.
        self.runGame()


    #Player can bid or challenge
    def PlayerTurn():
        while 1:
            print gameMessage["previous_bid"]
            print gameMessage["user_turn"]
            inputAction = raw_input('-->')
            inputAction = sting.upper(inputAction)
            if () or ():
                return False
                break
            if (inputAction == 'B')
                self.makeBid()
            else if (inputAction == 'C')
                self.challengeRequest()
            else:
                self.gameMessages["invalid_action"]


    #Client sends bid to server
    def makeBid():
        print gameMessage["previous_bid"] % (self.previousBid["quantity"], self.previousBid["value"])
        #Get the quantity
        this.player.getBidQuantity()
        this.player.getBidValue()
        #Check if valid bid or restart
        if (!self.checkBid()){
            print sendMessage[""]
            self.playerTurn()
            return
        }
        #Send message to server


    #Check the player's current bid against the previous bid values
    def checkBid():
        
        quantity = self.player.currentBid["quantity"]
        value = self.player.currentBid["value"]
        prevQuantity = self.previousBid["quantity"]
        prevValue = self.previousBid["value"]

        #If neither quantity or value has increased or has decreased.
        if (quantity == prevQuantity) and (value == prevValue):
            return False
        #Quantity is higher than the current total of dice in game.
        if (quantity > self.getTotalDiceQuantity()):
            return False
        #Face value is lower or higher than regular dice
        if (value < 1 ) or (value > 6):
            return False
        return True


    #Client sends challenge request to server
    def challengeRequest():
        print gameMessage["you_challenge"] % (self.previousPlayerName)
        print gameMessage["previous_bid"]
        #Send message to server
        challengeRequest = '[challenge, %s]', self.player.id
        self.clientsocket.send(challengeRequest)
        #Wait for server to respond to request
        self.runGame()


    #Sends request to quit to server.
    def quitGame():
        print gameMessages["end_thanks"]
        quitmsg = '[quit,%s]' % (self.player.name)
        self.connection.sendMessage(quitmsg)
        exit()


    #Main game loop, waits for server to send messages.
    #When message is received, parse and take action or wait
    #TODO add server timeout handling
    def runGame():
        while 1:
            #Wait for message from server.
            message = self.Connection.getMessage()
            #TODO Check if message is a valid array
            self.parsedMessage = message
            #Determine what message to show client and avaiable actions
            self.manageMessage()


    #Switch statement for received messages
    def manageMessage():
        reponseType = self.parsedMessage[0]
        if (reponseType == 'player_joined'):
            #TODO
        else if (reponseType == 'client_quit'):
            self.clientQuit()
        else if (reponseType == 'client_kicked'):
            self.clientKicked()
        else if (reponseType == 'timer_start'):
            self.timerStart()
        else if (reponseType == 'round_start'):
            self.roundStart()
        else if (reponseType == 'client_joined'):
            self.clientJoinedServer()
        else if (reponseType == 'your_dice'):
            self.showYourDice()
        else if (reponseType == 'player_turn'):
        else if (reponseType == 'round_end'):
        else if (reponseType == 'game_end'):
        else if (reponseType == 'bid_report'):
        else if (reponseType == 'invalid_move'):
        else if (reponseType == 'player_turn'):
        else if (reponseType == 'state'): #State of the server (lobby, lobby with countdown, game in session)
            self.showStatus()
        else: #Invalid message received 
            print gameMessages["invalid_received"]
        

    #Sets player id/order number, displays status of server
    #Options: In Game, Waiting In Lobby, Waiting In Lobby With Countdown
    #TODO Cancel countdown status
    def showStatus():
        self.player.id = self.parsedMessage[2]
        print gameMessages["order_number"] % (self.player.id)
        if (self.parsedMessage[1] == 'lobby'):
        else if (self.parsedMessage[1] == 'lobby_with_timer'):
        else if (self.parsedMessage[1] == 'in_game'):
        else:
            print gameMessages["invalid_received"]


    #TODO, message sent to client needs to be relooked at...
    def getOpponentNamesFromStatus():


    def showYourDice():


    def clientQuit():
        print gameMessages["client_quit"] % (self.parsedMessage[1])
        #TODO remove opponent from self.opponents array
    
    #TODO Check if self.parsedMessage[1] is name or id
    #TODO Handle if to few people remaining in game to finish
    def clientKicked():
        #You have been kicked out
        if (self.parsedMessage[1] == self.player.id):
            print gameMessages["you_kicked"]
            if (autoMode):
                self.QuitGame()
        #Other player has been kicked out
        else :
            print gameMessages["player_kicked"] % (self.parsedMessage[1])
    
    def timerStart():
        print gameMessages["timer_start"] % self.parsedMessage[1]
    
    def roundStart():
        #Reset the bid to 0.
        self.previousBid = {"quantity": 0, "value": 0}
        print gameMessages["round_begin"]
        self.totalDice = 0
        #TODO: display quanitity number of each player's dice, record the total number of dice in game.
        print gameMessages["total_dice"] % (self.totalDice)
        print gameMessages["reset_bid"] 
    
    def clientJoinedServer():







#########################################################################################
#########################################################################################
        
                
 
    #ClientJoined
                #Need to add person to spl
                elif MsgArray[q][0] == "client_joined":
                    if MsgArray[q][1] == self.MyName:
                        print 'You have joined the server.'
                        self.MyPlayerNo = MsgArray[q][2]
                    else:
                        print "Player " + self.GetNumName(MsgArray[q][2]) + " has joined the server."
                    newplayer = ServerPeople(MsgArray[q][1],MsgArray[q][2])
                    self.Spl.append(newplayer)
                    
    #YourDice  
                elif MsgArray[q][0] == "your_dice":
                    print "You, "+ self.MyName + ", currently have " + MsgArray[q][1] + " dices."
                    for x in range(2,len(MsgArray[q])):
                        print 'Dice no.' + str(x-1) + ' : ' + MsgArray[q][x]
                    
    #PlayerTurn 
                elif MsgArray[q][0] == "player_turn":
                    if MsgArray[q][1] != self.MyPlayerNo:
                        playert = self.GetNumName(MsgArray[q][1])
                        print "It is now " + playert + "'s turn.\n"
                    else:
                        print 'It is now your turn.\n'
                        self.State = "In_Game"

    #Round End - After a Challenge is done loser is determined.
                elif MsgArray[q][0] == "round_end":
                    self.PrevBid = [0,0]
                    print "Aftermath of challenge:"
                    print self.GetNumName(MsgArray[q][1]) + " has lost the round and a die.\n"
                    print "The following dice ammount for each player was:"
                    co = 2
                    while 1:
                        print 'Player ' + self.GetNumName(MsgArray[q][co]) + ' had ' + MsgArray[q][co+1] + ' dice:'
                        for x in range (0,int(MsgArray[q][co+1])):
                            print str(MsgArray[q][co+1+x]) + " "
			co += int(MsgArray[q][co+1])+2
			if co >= len(MsgArray[q]):
			    break
		    print '\n'

    #Game End 
                elif MsgArray[q][0] == "game_end":
                    playert = self.GetNumName(MsgArray[q][1])
                    print 'The game has ended; the winner is: ' + playert + "!"
                    if MsgArray[q][1] == self.MyPlayerNo:
                        print 'You have been moved back to the lobby.'
                        self.State = "Waiting"

    #Bid Report
                elif MsgArray[q][0] == "bid_report":
                    playert = self.GetNumName(MsgArray[q][1])
                    print 'Player '+ playert +' has bid '+ MsgArray[q][2] +" "+ MsgArray[q][3] +"'s.\n"
                    self.PrevBid[0] = int(MsgArray[q][2])
                    self.PrevBid[1] = int(MsgArray[q][3])

    #Bidding State
                if self.State == "In_Game":
                    
                    if MsgArray[q][0] == "invalid_move":
                        print 'Sever found that move was invlaid. ' + MsgArray[q][1] + ' tries allowed left.'
                        if int(MsgArray[q][1]) != 0:
                            MsgArray[q][0] = "player_turn"
			    MsgArray[q][1] = self.MyPlayerNo
                        #Server will resend player_turn to keep order straight.

                    if MsgArray[q][0] == "player_turn":
                        if MsgArray[q][1] == self.MyPlayerNo:
                            bidno = 0
                            bidval = 0
                            print 'It is your turn! Bid or Challenge? (B/C):'
                            if self.AutoMode == True:
                                action = random.choice('BBC') #Autoplay usually chooses to bid more.
                                print '-->' + action
                            else:
                                action = raw_input('-->')
                            while 1:
                                if (string.upper(action) == "QUIT") or (string.upper(action) == "Q"):
                                    self.QuitGame()
                                    break
                                elif string.upper(action) == "B" or string.upper(action) == "C":
                                    break
                                else:
                                    print 'Answer is invald. Try again: '
                                    action = raw_input('-->')
                                    
                            if string.upper(action) == "B":
                                print 'The previous dice face bid was: ' + str(self.PrevBid[1]) + '.'
                                print 'Enter the dice face value you want to bid: '
                                if self.AutoMode == True:
                                    bidval = str(random.randint(self.PrevBid[1],6))
                                    print '-->' + bidval
                                else:
                                    bidval = raw_input('-->')
                                while 1:
                                    try:
                                        if (string.upper(bidval) == "QUIT") or (string.upper(bidval) == "Q"):
                                            self.QuitGame()
                                            break
                                        if (int(bidval) > 0) and (int(bidval) < 7):
                                            bidval2 = int(bidval)
                                            break
                                        else:
                                            print 'Incorrect value for bid, pick a face value: '
                                            if self.AutoMode == True:
                                                bidval = str(random.randint(self.PrevBid[1],6))
                                                print '-->' + bidval
                                            else:
                                                bidval = raw_input('-->')
                                    except:
                                        print 'Incorrect value for bid, pick a face value: '
                                        bidval = raw_input('-->')
                                print 'The previous dice ammount bid was: ' + str(self.PrevBid[0]) + '.'
                                print 'Enter the number of dice you want to bid: '
                                if self.AutoMode == True:
                                    gpcount = 0
                                    for x in range(0,len(self.Spl)):
                                        if self.Spl[x].InGame == True:
                                            gpcount += 1
                                    if int(bidval) > self.PrevBid[0]:
                                        bidno = str(random.randint(1,self.dicepool))
                                    else:
                                        bidno = str(random.randint(self.PrevBid[0],self.dicepool))
                                    print '-->' + bidno
                                else:
                                    bidno = raw_input('-->')
                                while 1:
                                    try:
                                        if (string.upper(bidno) == "QUIT") or (string.upper(bidno) == "Q"):
                                            self.QuitGame()
                                            break
                                        elif (int(bidno) > 0) and (int(bidno) < 100):
                                            bidno2 = bidno
                                            break
                                        else:
                                            print 'Incorrect value for bid, pick an ammount of dice: '
                                            if self.AutoMode == True:
                                                gpcount = 0
                                                for x in range(0,len(self.Spl)):
                                                    if self.Spl[x].InGame == True:
                                                        gpcount += 1
                                                        print gpcount
                                                if int(bidval) > self.PrevBid[0]:
                                                    bidno = str(random.randint(1,self.dicepool))
                                                else:
                                                    bidno = str(random.randint(self.PrevBid[0],self.dicepool))
                                                print '-->' + bidno
                                            else:
                                                bidno = raw_input('-->')
                                    except:
                                        print 'Incorrect value for bid, pick an ammount of dice: '
                                        if self.AutoMode == True:
                                            gpcount = 0
                                            for x in range(0,len(self.Spl)):
                                                if self.Spl[x].InGame == True:
                                                    gpcount += 1
                                                    print gpcount
                                            if int(bidval) > self.PrevBid[0]:
                                                bidno = str(random.randint(1,self.dicepool))
                                            else:
                                                bidno = str(random.randint(self.PrevBid[0],self.dicepool))
                                            print '-->' + bidno
                                        else:
                                            bidno = raw_input('-->')
                                bidmsg = '[bid,%s,%s]' % (bidno,bidval)
                                self.clientsocket.send(bidmsg)


                            if string.upper(action) == "C":
                                self.clientsocket.send("[challenge]")
                                

                    
                
                
        self.clientsocket.close()
            
s = Client('localhost', 36712)
s.run()
    
