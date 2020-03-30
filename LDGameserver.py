import socket, select, string, threading, random, sys


###############################################################################
#Natalie Kiner, W00846843
#CSCI 367 - Winter 2012
#March 13th 2012
#
#Lair's Dice socket server. Works with corresponding Lair's Dice socket clients
#using a uniform messaging standard. Server collects clients and waits until 
#3-5 players have joined. After a timer ends, the game begins with the players
#found.
###############################################################################

#Record that contains info about one player in a currently running game.

class InGameInfo:
    def __init__(self,HostPort,Pname,Dice, Order):
        self.HP = HostPort #contains player's host/port identifier
        self.Pname = Pname #contains player's name
        self.Dice = Dice #contains array of player's dice
        self.DiceNo = 5 #Each player starts with 5 dice   
        self.OutofPlay = False #They are currently in_game, not just watching
        self.Order = Order #determines order of players
        


#Record that contains info about one player's current status on the server.
        
class ClientState:
    def __init__(self, HostPort,Pname,State, Order):
        self.HP = HostPort #contains the client's host/port identifier
        self.Pname = Pname #has name of player that joined
        self.State = State #contains a string of the client's current state
        self.Order = Order #determines order of players
        


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



#Takes a Message sent from the client and decodes it into an array of strings
#It is assumed one message will be sent at a time from each client.
    def MsgDecode(self, pstring):
        x = ' '
        StrBuild = ""
        DecodedArray = []
        for y in range(0,len(pstring)):
            if pstring[y] == '[':
                if y > 0:
                    StrBuild += pstring[y]
            elif pstring[y] == ',':
                DecodedArray.append(StrBuild)
                StrBuild = ""
            elif pstring[y] == ']':
                if y < (len(pstring)-1):
                    StrBuild += pstring[y]
                else:
                    DecodedArray.append(StrBuild)
            else:
                StrBuild += pstring[y]
        return DecodedArray
    
##############################################################################
#Takes a Message sent from the client and decodes it into an
#array of array of strings.
    def MsgDecode2(self,pstring):
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

    
#Get Name Using Rank/Order Number
    def GetNumName(self, number):
        name = ""
        for x in range(0,len(self.ClientState)):
            if self.ClientState[x].Order == number:
                name = self.ClientState[x].Pname
                break
        return name         
        

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
        
        
        
        


#O#Remove from playing game, but not from the server. Should be able to go back to lobby when finished.      
    def KickPlayer(self, HP):
        self.AttemptCount = 5
        for x in range(0,len(self.InGameInfoA)):
            if self.InGameInfoA[x].HP == HP:
                self.InGameInfoA[x].Dice = []
                print 'Player %s has been removed from play.\n' % (self.InGameInfoA[x].Pname)
                kickmsg = '[client_kicked,%s]' % (self.InGameInfoA[x].Order)
                self.broadcast(kickmsg) 
                for y in range(0,len(self.ClientState)):
                    if self.ClientState[y].HP == HP:
                        self.ClientState[y].State = "lobby"
                self.InGameInfoA.pop(x)
                break
        if (len(self.InGameInfoA) == 1):
            self.EndGame(self.InGameInfoA[0].HP)
        elif (self.SvrState == "In_Game") and (len(self.InGameInfoA) > 0):
            self.NextTurn(self.Order)
        

#X#When game ends, remove InGameInfo, switch client states to lobby and switch SvrState back to lobby.
    def EndGame( self, winnerHP ):
        for x in range(0,len(self.InGameInfoA)):
            if self.InGameInfoA[x].HP == winnerHP:
                winnerNum = self.InGameInfoA[x].Order
            for y in range(0, len(self.ClientState)):
                if self.InGameInfoA[x].HP == self.ClientState[y].HP:
                    self.ClientState[y].State = "lobby"
                    self.InGameInfoA.pop(x)
                    print self.ClientState[y].Pname + ' has returned to the lobby.\n'
                    break
        print "The game has ended. The winner is " + self.GetNumName(winnerNum) + "!\n"
        winnermsg = "[game_end,%s]" % (winnerNum)
        self.broadcast(winnermsg)
        self.PreviousBid = [0,0]
        self.SvrState = "Waiting"
        self.checkplayers()
        

        
#X#Kicks out a client by first determining it's state and then taking appropriate action.
    def PlayerQuit( self, Pname):
        for x in range(0,len(self.InGameInfoA)):
            print self.InGameInfoA[x].Pname
            if self.InGameInfoA[x].Pname == Pname:
                HP = self.InGameInfoA[x].HP
                self.InGameInfoA.pop(x)
                print 'Player ' + Pname + ' was in game and is now quitting...'
                for sock in self.descriptors:
                    if sock != self.srvsock:
                        if sock.getpeername() == HP:
                            sock.close()
                            self.descriptors.remove(sock)
                            print 'The client socket has been closed.'
                            break
                break
        for x in range(0,len(self.ClientState)):
            if self.ClientState[x].Pname == Pname:
                Pnum = self.ClientState[x].Order
                if Pnum == self.Order:
                    if Pnum >= len(self.InGameInfoA)-1:
                        self.Order = 0
                    else:
                        self.Order = self.Order + 1
                HP = self.ClientState[x].HP
                print 'Player has now left the game...'
                quitmsg = '[client_quit,%s]' % (Pnum)
                self.broadcast(quitmsg)
                self.ClientState.pop(x)
                break
        self.printply()
        if (len(self.InGameInfoA) == 1):
            self.EndGame(self.InGameInfoA[0].HP)
        elif self.SvrState == "In_Game":
            if len(self.InGameInfoA) > 0:
                self.NextTurn(self.Order)
                
#O#Random Dice Generator, takes in number of dice player has and generates
#an array of that size of dice from 1 to 6.

    def DiceGen(self, diceno):
        dicearray = []
        for x in range(0,diceno):
            y = random.randint(1,6)
            dicearray.append(y)
        return dicearray

#~#Sends round end to all players and removes die from loser/gets rid of loser.
#MERGE to DetermineWinner. Send Round_End Message and remove dice from player.
#If player has no dice than kick him out.
    
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


#X#Checks challenge to determine if the current player is a winner or not.
    
    def DetermineWinner(self):
        dicearray = [0,0,0,0,0,0]
        for x in range(0,len(self.InGameInfoA)):
            for y in range(0,len(self.InGameInfoA[x].Dice)):
                if self.InGameInfoA[x].Dice[y] == 1:
                    dicearray[0] += 1
                elif self.InGameInfoA[x].Dice[y] == 2:
                    dicearray[1] += 1
                elif self.InGameInfoA[x].Dice[y] == 3:
                    dicearray[2] += 1
                elif self.InGameInfoA[x].Dice[y] == 4:
                    dicearray[3] += 1
                elif self.InGameInfoA[x].Dice[y] == 5:
                    dicearray[4] += 1
                elif self.InGameInfoA[x].Dice[y] == 6:
                    dicearray[5] += 1
        print 'The results are: \n'
        for x in range(0,6):
            print str(x+1) + ': ' + str(dicearray[x]) + ' dices.'

        print "The order of players went: " + self.ordercheck
        self.ordercheck = ""

        if dicearray[self.PreviousBid[1]-1] < self.PreviousBid[0]:
            #Challenger wins
            winner = self.findranking(self.Order)
            losername = ""
            if (self.Order == 0):
                loser = self.findranking(self.Order)
                losername = self.ClientState[self.Order].Pname	
            else:
                loser = self.findranking(self.Order-1)
                losername = self.ClientState[self.Order-1].Pname
            self.ShowDice(winner, loser)
            print 'Previous player '+ losername +' bid: ' + str(self.PreviousBid[0]) + ' ' + str(self.PreviousBid[1]) + "'s,"
            print 'and was caught cheating!'
			
            
        else:
            loser = self.findranking(self.Order)
            if (self.Order == 0):
                winner = self.findranking(self.Order)
            else:
                winner = self.findranking(self.Order-1)
            #Challenger loses
            self.ShowDice(winner, loser)
            print 'Previous player bid: ' + str(self.PreviousBid[0]) + ' ' + str(self.PreviousBid[1]) + "'s,"
            print 'and was not cheating!'
        if len(self.InGameInfoA) == 1: #Only one player left, announce winner.
            self.PreviousBid = [0,0]
            self.EndGame(self.InGameInfoA[0].HP)
        else:
            #Propagate next round.
            self.PreviousBid = [0,0]
            self.BeginGame()
            
            
            

        
#O#Broadcasting Messages to Everyone
    def broadcast(self, bstring):
        for sock in self.descriptors:
            if sock != self.srvsock:
                sock.send(bstring)

#O#Send Message to specific client
    def sendmsg(self, mstring, hostport):
        for sock in self.descriptors:
            if sock != self.srvsock:
                if sock.getpeername() == hostport:
                    sock.send(mstring)
                    break

#Finds the nth biggest PlayerNumber(Their Order) in a InGameInfoA
    def findranking(self, rank):
        if rank >= len(self.InGameInfoA):
            rank = (len(self.InGameInfoA)-1)
        numlist = []
        for x in range(0,len(self.InGameInfoA)):
            numlist.append(self.InGameInfoA[x].Order)
        numlist.sort()
        return numlist[rank]
    
#O#Finds which player goes next by order and sends message with that player's name.
    def NextTurn(self, order):
        if len(self.InGameInfoA) == 1:
            self.EndGame(self.InGameInfoA[0].HP)
        else:
            SrtPnum  = self.findranking(order)
            self.ordercheck += str(SrtPnum)
            print 'Player ' + self.GetNumName(SrtPnum) + ' is going next.'
            plturnmsg = '[player_turn,%s]' % (SrtPnum)
            self.broadcast(plturnmsg)
    

    def checkplayers(self):
        if len(self.ClientState) >= self.MinPlayers: #at least 2 players needed
            for x in range(0, len(self.ClientState)):
                if len(self.InGameInfoA) < self.MaxPlayers: #up to 5 players can be handled
                    self.ClientState[x].State = "lobby_with_timer"
                    Ord = self.ClientState[x].Order
                    Pnm = self.ClientState[x].Pname
                    newplayerinfo = InGameInfo(self.ClientState[x].HP,Pnm,self.DiceGen(5),Ord)
                    self.InGameInfoA.append(newplayerinfo)
            strpc = str(len(self.InGameInfoA))
            timemsg = '[timer_start,%s]' % (self.GameWTimer)
            self.broadcast(timemsg)
            print strpc + " have joined, "+ str(self.GameWTimer)+ " seconds until game starts.\n"
            self.SvrState = "TimerWait"
            try:
                self.waitt.start()
            except:
                self.waitt.cancel()
                self.waitt = threading.Timer(self.GameWTimer, self.BeginGame)
                self.waitt.start()
            

#Shows how many people are at what state on the server.
    def printply(self):
          svrstr = 'Players on server: '
          if len(self.ClientState) != 0:
              svrstr += self.ClientState[0].Pname
              for x in range(1,len(self.ClientState)):
                  svrstr += ',' + self.ClientState[x].Pname
              print svrstr
          else:
            print svrstr + 'None'
        
          gamstr = 'Players in Game: '
          if len(self.InGameInfoA) != 0:
              gamstr += self.InGameInfoA[0].Pname
              for x in range(1,len(self.InGameInfoA)):
                  gamstr += ',' + self.InGameInfoA[x].Pname
              print gamstr + '\n'
          else:
            print gamstr + 'None\n'

        
##############################################################################
#Main Server Game Loop

        
    def run( self ):
        
      print "The Lair's Dice Server has Started Running.\n"

      argbound = False
      for x in range(0,len(sys.argv)):
          if (sys.argv[x] == "-p"):
              argbound = True
              self.srvsock.bind( ("", sys.argv[x+1]) ) #Connects to the requested port.
          elif (sys.argv[x] == "-m"):
              self.MinPlayers = sys.argv[x+1]
          elif (sys.argv[x] == "-M"):
              self.MaxPlayers = sys.argv[x+1]
          elif (sys.argv[x] == "-t"):
              self.LobbyWTimer = sys.argv[x+1]
          elif (sys.argv[x] == "-a"):
              self.AttemptCount = sys.argv[x+1]
              self.AC = sys.argv[x+1]

      if argbound == False:
          self.srvsock.bind( ("", self.port) ) #Connects to default port, self.port.
      self.srvsock.listen( 5 )
          
            
              
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
                if str1 == '':
                    for x in range(0,len(self.ClientState)):
                        if (sock != self.srvsock):
                            if (self.ClientState[x].HP == sock.getpeername()):
                                Pname = self.ClientState[x].Pname
                                break
                    self.PlayerQuit(Pname)
                    MsgArray = [[""]]
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
