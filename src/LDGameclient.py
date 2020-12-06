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

    #lobby and joining game status
    "enter_name": "Please enter your name (1-10 characters): ",
    "connecting" : "Connecting to server...\n",
    "connection_timeout": "Server took too long to respond. That's a shame.\n",
    "connected" : "You have connected to the server.\n",
    "joined_lobby": "You have joined the lobby.\n",
    "you_joined_lobby": "You have joined the lobby.\n",
    "player_joined" : "%s has joined the lobby.\n",
    "lobby_status": 'Currently the server is waiting for more clients.',
    "names_list" : 'Players on the server: %s',
    "lobby_timer_status" :'Currently the server has enough clients and waiting for the game to begin.',
    "timer_start" : "A new Lair's Dice game will begin in %s seconds.",
    "in_game_status" : 'Currently there is a game already running on the server.',

    #starting new game messages
    "your_dice": "You currently have %s dice: %s",
    "order_number": "Your order number is %s.\n",

    #round start status
    "round_begin" : 'The round has begun with %s players.',
    "previous_bid": "The previous player bid %s dice with %s value.\n",
    "total_dice" : "The total number of dice among players is %s",
    "reset_bid" : "The bid on dice has been reset to 0.",

    #your turn action messages
    "your_turn" : "It is now your turn.",
    "user_turn": "It is your turn! Bid or Challenge? ('B' or 'C')\n",
    "you_bid" : "You have bid %s dice of value %s\n",
    "bid_quantity": "How many dice will you bid?\n",
    "bid_value": "What value of dice will you bid?\n",
     "invalid_bid": "The bid %s dice of %s value does not work with the previous bid of %s dice of %s value. Please try again.\n",
    "you_challenge": "You have challenged %s's bid!\n"
    "invalid_action" : "The action is invalid, please try again.",
    "server_invalid_move" : "The move sent was invalid, please try again. (%s attempts remaining)"
    
    #opponent turn action messages
    "player_turn" : "It is now %s's turn.\n",
    "player_bid" : "Player %x bid %s dice of value %s.\n",
    "challenge": "%s has challenged %s!\n",

    #turn aftermath messages
    "challenge_after": "Aftermath of challenge: \n%s has lost the round and a die.\nThe following dice ammount for each player was: ",
    "player_dice" : "Player %s had dice: ",
    "turn_change": "It is now %s turn.\n",

    #game ends messages
    "game_end" : "The game has ended, the winner of Liar's Dice is %s!",
    "end_thanks" : "Thank you for playing Liar's Dice!\n",
    "lobby_return" : "You have been moved back to the lobby.",

    #qutting and kicking messages
    "player_quit": "Player %s has quit the game\n",
    "player_kicked": "Player %s has been kicked out of the game!\n",
    "you_quit": "Thank you for playing!\n",
    "you_kicked" : "You have been kicked out of the game! Better luck next time!\n",

    #other error messages
    "invalid_received" : "Invalid message has been received from the server. Moving on...\n"

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

#TODO make player id seperate from order number, randomize the player id client receives.
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


    #TODO Get total dice from the server instead of calculating here.
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
        
        #Ask if player wants to use AutoPlay mode
        self.setAuto()

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
        self.connection.sendMessage(joinRequest)
        #Go to main game loop and wait for server messages.
        self.runGame()


    #Choose to bid or challenge
    def yourTurn():
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
        quantity = self.player.currentBid["quantity"]
        value = self.player.currentBid["value"]
        message = "[player_bid,%s,%s,%s]" % (self.player.id, quantity, value)
        self.connection.sendMessage(message)


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
        self.connection.clientsocket.send(challengeRequest)
        #Wait for server to respond to request
        self.runGame()


    #Sends request to quit to server.
    def quitGame():
        print gameMessages["end_thanks"]
        quitmsg = '[quit,%s]' % (self.player.name)
        self.connection.sendMessage(quitmsg)
        self.connection.clientsocket.close()
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
            self.playerTurn()
        else if (reponseType == 'round_end'):
            self.roundEnd()
        else if (reponseType == 'game_end'):
            self.gameEnd()
        else if (reponseType == 'bid_report'):
            self.bidReport()
        else if (reponseType == 'invalid_move'):
            self.invalidMove()
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
    

    #Displays that you or an opponent has joined the server's lobby.
    def clientJoinedServer():
        if (self.parsedMessage[1] == self.player.name):
            print sendMessages["joined_lobby"]
            self.player.id = self.parsedMessage[2]
        else:
            print gameMessages["player_joined"] % ( self.parsedMessage[2] ) + " has joined the server."
            opponent = Opponent(self.parsedMessage[1],self.parsedMessage[2])
            self.opponents.append(opponent)


    #Displays your current dice.
    def yourDice():
        quantity = self.parsedMessage[1]
        values = ""
        for x in range(2,len(self.parsedMessage)):
                values +=  self.parsedMessage[x] + " "
        print gameMessages["your_dice"] % (quantity, values)


    #Determine whether your turn or opponents turn.
    def playerTurn():
        if self.parsedMessage[1] != self.player.id:
            #Get opponent name from opponents array?
            playerName = self.GetNumName(self.parsedMessage[1])
            print gameMessages["player_turn"] % (playerName)
        else:
            print gameMessages["your_turn"]
            self.yourTurn()
    

    def roundEnd():
            #TODO Redundant reset of previous bid, already done in roundStart()
            self.previousBid = {"quantity": 0, "value": 0}
            
            #Get the losing player's name from id
            playerName = self.GetNumName(self.parsedMessage[1])
            print gameMessages["challenge_after"] % (playerName)

            #Display each player's dice
            i = 2
            while (i >= len(self.parsedMessage)):
                #Get the player's name by id
                playerName = self.GetNumName(self.parsedMessage[i])
                print gameMessages["player_dice"] % (playerName)
                for x in range (0,len(self.parsedMessage[i+1])):
                    print str(self.parsedMessage[i+1+x]) + " "
                print '\n'
			    i += int(self.parsedMessage[i+1])+2
    

    def gameEnd():
        #Get the winning player's name and display it.
        playerName = self.GetNumName(self.parsedMessage[1])
        print gameMessages["game_end"] % (playerName)
        #Player is returned to lobby
        print gameMessages["lobby_return"]


    #Display new bid and update previous bid variable's quantity and value.
    def bidReport():
        #Display your bid
        if (self.parsedMessage[1] == self.player.id):
            print gameMessages["you_bid"] % (self.parsedMessage[2], self.parsedMessage[3])
        #Display player's bid
        else:
            playerName = self.getNameFromId(self.parsedMessage[1])
            print gameMessages["player_bid"] % (playerName, self.parsedMessage[2], self.parsedMessage[3])
        #Update the previous bid value with new bid
        self.previousBid["quantity"] = int(self.parsedMessage[2])
        self.previousBid["value"] = int(self.parsedMessage[3])
    
    #TODO something about keeping track of attempts and server resending player move request
    def invalidMove():
        print gameMessages["server_invalid_move"] % (self.parsedMessage[1])


#############################################################################################

#Create new instance of the gameclient and start the game.
gameClient = gameClient()
gameClient.joinGame()

    
