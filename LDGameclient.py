import socket, sys, string, random

###############################################################################
#Natalie Kiner, W00846843 
#CS 367 - Winter 2012
#March 13th 2012
#
#Lair's Dice Client. Connects with the Liar's Dice Server and recieves/gives
#messages over a socket to interact in the game.
###############################################################################



class ServerPeople:
    def __init__(self, name, number):
        self.Pname = name
        self.Number = number
        self.InGame = False
    

class Client:
    def __init__( self, host, port):
        self.port = port;
        self.host = host;
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.State = "Connect" #Contains states of the client
        self.Spl = [] #Array of SeverPeople records
        self.MyName = "aaaaaaaaaaaa" #Name of player, changed when joining server.
        self.MyPlayerNo = 200 #Number assigned after giving name to server.
        self.AutoMode = False #Automatic Play thingy
        self.PrevBid = [0,0]
        self.dicepool = 0 #The total number of dice in play, used for A.Mode bidding.
                                

##############################################################################
#Takes a Message sent from the client and decodes it into an
#array of array of strings.
    def MsgDecode(self,pstring):
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

        
##############################################################################
    def QuitGame(self):
        print 'Thank you for playing!'
        quitmsg = '[quit,%s]' % (self.MyName)
        self.clientsocket.send(quitmsg)
        exit()

##############################################################################

    def RandomName(self):
        name = ''
        namelength = random.randint(1,9)
        for x in range(0,namelength):
            name += random.choice(string.ascii_lowercase)
        return name

##############################################################################
        
    def GetNumName(self, number):
        name = ""
        for x in range(0,len(self.Spl)):
            if self.Spl[x].Number == number:
                name = self.Spl[x].Pname
                break
        return name
            
   
    def run ( self ):
        print 'Would you like to turn Auto-play on? (Y/N): '
        autostr = raw_input('-->')
        autostr = string.upper(autostr)
        if (autostr == 'Y') or (autostr == 'YES'):
            print 'Auto-play has been turned on.\n'
            self.AutoMode = True
        else:
            print 'Auto-play is off.\n'

        print 'Now connecting to server at host: %s, port: %s\r\n' % (self.host, self.port)
        while True:
            try:
                print 'Connecting...\n'
                self.clientsocket.connect((self.host, self.port))
                break
            except:
                while True:
                    print 'Cannot connect to sever. Retry? Y/N'
                    str2 = raw_input('-->')
                    if ((string.upper(str2) == 'N') or (string.upper(str2) == 'NO')):
                        print 'Now exiting the program...\n'
                        exit()
                    else:
                        print 'Reattempting to connect...\n'
                        break
                    
        print "You have now connected to a socket!\n"
        while 1:
            print "Enter your name (1-10 characters): "
            if self.AutoMode == True:
                str1 = self.RandomName()
            else:
                str1 = raw_input('-->')
            if string.upper(str1) == "QUIT":
                self.QuitGame()
            elif (len(str1) > 10) or (len(str1) == 0):
                print 'Number of letters entered out of range. Try again.'
            else:
                break
        self.MyName = str1
        JoinMessage = '[join,%s]' % (str1)
        self.clientsocket.send(JoinMessage)
        
        while 1:


            msgstring = self.clientsocket.recv(1024)
            MsgArray = self.MsgDecode(msgstring)

            print MsgArray
            print ''
            
            for q in range(0,len(MsgArray)):
                ##If MsgArray[x][1] == "banana": ect.
                
    #State
                if MsgArray[q][0] == "state":
                    self.MyPlayerNo = MsgArray[q][2]
                    print 'Your order number is ' + str(self.MyPlayerNo)

                    
                    if MsgArray[q][1] == "lobby":
                        print 'Currently the server is waiting for more clients.'
                    elif MsgArray[q][1] == "lobby_with_timer":
                        print 'Currently the server has enough clients and waiting\n'
                        print 'for the game to begin.'
                    elif MsgArray[q][1] == "in_game":
                        print 'Currently there is a game already running on the server.'
                    print 'Current names of people on server: '
                    if len(MsgArray[q])-3 == 0:
                        print 'None'
                    else:
                        c = 3
                        while c < len(MsgArray[q]):
                            newperson = ServerPeople(MsgArray[q][c],MsgArray[q][c+1])
                            self.Spl.append(newperson)
                            print MsgArray[q][c]
                            c = c + 2
                    
                        
    #ClientQuit                    
                elif MsgArray[q][0] == "client_quit":
                    print 'Player ' + self.GetNumName(MsgArray[q][1]) + " has left the server."
                    for x in range(0,len(self.Spl)):
                        if self.Spl[x].Number == MsgArray[q][1]:
                            self.Spl.pop(x)
                            break
    #ClientKicked
                elif MsgArray[q][0] == "client_kicked":
                    if MsgArray[q][1] == self.MyPlayerNo:
                        print 'You have been kicked out of the game!'
                        self.State = "Waiting"
                        if self.AutoMode == True:
                            self.QuitGame()
                    else:
                        print 'Player ' + self.GetNumName(MsgArray[q][1]) + " has been kicked out of game!"
                        for x in range(0,len(self.Spl)):
                            if self.Spl[x].Number == MsgArray[q][1]:
                                print "Since Automode is on, player has now quit the game."
                                self.Spl[x].InGame = False
                                break

                    
    #TimerStart                
                elif MsgArray[q][0] == "timer_start":
                    print 'New game will begin in ' + MsgArray[q][1] +' seconds.'
                    
    #RoundStart                
                elif MsgArray[q][0] == "round_start":
                    self.PrevBid = [0,0]
                    print 'Round has begun with ' + MsgArray[q][1] + ' players.'
                    self.dicepool = 0
                    counter = 2
                    while 1:
                        if counter >= len(MsgArray[q]):
                            break
                        else:
                            for x in range(0, len(self.Spl)):
                                if MsgArray[q][counter] == self.Spl[x].Number:
                                    self.Spl[x].InGame = True
                            print 'Player '+ self.GetNumName(MsgArray[q][counter]) +' has '+MsgArray[q][counter+1] +' dice.'
                            self.dicepool += int(MsgArray[q][counter+1])
                            counter = counter + 2
                    print 'The total number of dice is ' + str(self.dicepool) + '.\n'
                    print 'The bid has been reset to ' + str(self.PrevBid[0]) +" ,"+ str(self.PrevBid[1])
                            
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
    
