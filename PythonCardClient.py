#CLIENTTHREAD: UID1-inf
class client(Thread):
        def __init__ (self, channel,UID):
                Thread.__init__(self)
                self.channel=channel
                self.alive=True
                self.UID=UID
                self.Uname="N/A"
                self.state="START"
                #Cardiac
                global TotHiddenCards, TotShownCards, MissingCards, TotDealedHand, MinHand, TotCards, CardStack, OutCardStack, stage
                self.ready=False
                self.HiddenCards=[]
                self.ShownCards=[]
                self.HiddenCardsHidden=[1,2,3]
                self.Hand=[]
                foo=0
 
                while foo!=TotHiddenCards:
                        self.HiddenCards.append(CardStack.pop())
                        foo=foo+1
                foo=0
                while foo!=TotShownCards:
                        self.ShownCards.append(CardStack.pop())
                        foo=foo+1
                foo=0
                while foo!=TotDealedHand:
                        self.Hand.append(CardStack.pop())
                        foo=foo+1
                foo=0
 
        def send(self, msg):
                try:
                        self.channel.send(msg)
                except socket.error, e:
                        lasterror=e
                        print("Failed to send message, client: "+str(self.UID)+" lost connection?")
                        self.state="FAILEDSEND"
                        self.alive=False
 
        def ping(self):
                try:
                        self.channel.send("PING")
                        self.pong=None
                        timeout=time.clock()+10
                        while self.pong==None:
                                if time.clock()>timeout:
                                        self.pong=False
                                pass
                        if self.pong==True:
                                return time.clock()-(timeout-10)
                        else:
                                return False
                except socket.error, e:
                        print(e)
                        Error=e
                        return False
 
        def MESG(self, uid, msg):
                #From argument removed, can be done clientside instead
                self.send("MESG"+MsgSep+str(uid)+MsgSep+msg)
 
        def run(self):
                global Error, BError
                global TotHiddenCards, TotShownCards, MissingCards, TotDealedHand, MinHand, TotCards, CardStack, OutCardStack, stage, turn, turntable
                try:
                        self.send("UID"+MsgSep+str(self.UID))
                        time.sleep(1)
                        self.send("CLIST"+MsgSep+pickle.dumps(ServerListener.CList))
                        #ServerListener.broadcast("CList"+MsgSep+pickle.dumps(ServerListener.CList)
                except socket.error, e:
                        error=e
                        print("Failed to initialize UID "+str(self.UID))
                        self.state="INITFAIL"
                        self.alive=False
               
                self.clock=time.clock()
                while self.alive:
                        try:
                                data=self.channel.recv ( 200 )
                                try:
                                        datasplit=string.split(data,MsgSep)
                                        arg=datasplit[1:]
                                except IndexError, e:
                                        print("Bad behaviour from: "+str(self.UID)+" : "+str(self.getName()))
                                command=string.split(data,MsgSep)[0]
                                BError=data
                                if not data:
                                        print("Client disconnected: "+str(self.channel.getsockname()))
                                        self.alive=False
                                        self.state="DCONN"
                                else:
                                        if command=="MESG":
                                                print(str(self.UID)+":"+datasplit[1])
                                                self.channel.send("RECV"+MsgSep)
                                                ServerListener.broadcastMSG(self.Uname,str(self.UID),datasplit[1])
                                        elif command=="UNAME":
                                                print("User: "+self.Uname+": "+str(self.UID)+"changed name to: "+datasplit[1])
                                                self.Uname=datasplit[1]
                                                ServerListener.UpdateCList()
                                                ServerListener.broadcast("UNAME"+MsgSep+str(self.UID)+MsgSep+self.Uname)
                                        elif command=="PING":
                                                print("Ping recived from "+str(self.UID))
                                                self.pong=True
                                        elif command=="HAND":
                                                print("Player: "+self.Uname+" requesting hand, sending..")
                                                self.send("HAND"+MsgSep+pickle.dumps(self.Hand))
                                        elif command=="DECK":
                                                print("Player: "+self.Uname+" requesting player "+CThreads[int(datasplit[1])].Uname+"'s deck, sending..")
                                                self.send("DECK"+MsgSep+datasplit[1]+MsgSep+pickle.dumps(CThreads[int(datasplit[1])].ShownCards))
                                        elif command=="HDECK":
                                                print("Player: "+self.Uname+" requesting player "+CThreads[int(datasplit[1])].Uname+"'s Hdeck, sending..")
                                                self.send("HDECK"+MsgSep+datasplit[1]+MsgSep+pickle.dumps(CThreads[int(datasplit[1])].HiddenCardsHidden))
                                        elif command=="SWDECK":
                                                if stage==0:
                                                        print("Player: "+self.Uname+" switched his Hand: "+str(self.Hand[int(arg[0])])+" with his deck "+str(self.ShownCards[int(arg[1])]))
                                                        ServerListener.broadcast("SWDECK"+MsgSep+str(self.UID)+MsgSep+str(self.Hand[int(arg[0])])+MsgSep+str(self.ShownCards[int(arg[1])]))
                                                        foo=self.Hand[int(arg[0])]
                                                        bar=self.ShownCards[int(arg[1])]
                                                        self.Hand[int(arg[0])]=bar
                                                        self.ShownCards[int(arg[1])]=foo
                                        elif command=="READY":
                                                ServerListener.broadcast("READY"+MsgSep+str(self.UID))
                                                print("Player: "+self.Uname+" is ready")
                                                self.ready=True
                                                foo=True
                                                for x in CThreads:
                                                        if not CThreads[x].ready:
                                                                foo=False
                                                if foo==True:
                                                        print("All players are ready, stage 1")
                                                        stage=1
                                                        ServerListener.broadcast("STAGE"+MsgSep+str(stage))
                                                        foo=100
                                                        bar=100
                                                        for x in CThreads:
                                                                foobar=min(CThreads[x].Hand)
                                                                if foobar==1:
                                                                        foobar=10
                                                                if foobar==2:
                                                                        foobar=20
                                                                if foobar<foo:
                                                                        foo=foobar
                                                                        bar=CThreads[x].UID
                                                                print("         Checking player "+CThreads[x].Uname+", lowest card = "+str(foo))
                                                        print("Player: "+CThreads[bar].Uname+" had the lowest card of "+str(foo))
                                                        turn=bar
                                                        foofight=0
                                                        turntable=[]
                                                        for x in CThreads:
                                                                foofight=foofight+1
                                                                turntable.append(x)
                                                        ServerListener.broadcast("PRINT"+MsgSep+"Player: "+CThreads[bar].Uname+" had the lowest card of "+str(foo))
                                                        barfoo=CThreads[bar].Hand.pop(CThreads[bar].Hand.index(foo)) #Remove the card from the players hand
                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                        CThreads[bar].Hand.append(CardStack.pop()) #Add a new card to the hand from the cardstack
                                                        ServerListener.broadcast("DEAL"+MsgSep+str(bar)+MsgSep+str(foo))
                                                        if turntable.index(turn)==len(turntable)-1:
                                                                turn=turntable[0]
                                                        else:
                                                                turn=turntable[turntable.index(turn)+1]
                                        elif command=="DEAL":
                                                if stage==1 and turn==self.UID:
                                                        print(arg[0])
                                                        if len(self.Hand)!=0:
                                                                if int(arg[0]) in self.Hand:
                                                                        foo=int(arg[0]) #Card being dealt
 
                                                                        if len(OutCardStack)!=0:
                                                                                bar=OutCardStack[len(OutCardStack)-1] #Last card dealt
                                                                        else:
                                                                                bar=0
 
                                                                        if foo==1: #Player dealt an ace
                                                                                barfoo=self.Hand.pop(self.Hand.index(foo)) #Remove the card from the players hand
                                                                                OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                if len(self.Hand)<MinHand and len(CardStack)!=0:
                                                                                        self.Hand.append(CardStack.pop()) #Add a new card to the hand from the cardstack
                                                                                if turntable.index(turn)==len(turntable)-1:
                                                                                        turn=turntable[0]
                                                                                else:
                                                                                        turn=turntable[turntable.index(turn)+1]
 
                                                                        elif foo==2: #Player dealt an "hold"
                                                                                barfoo=self.Hand.pop(self.Hand.index(foo)) #Remove the card from the players hand
                                                                                OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                if len(self.Hand)<MinHand and len(CardStack)!=0:
                                                                                        self.Hand.append(CardStack.pop()) #Add a new card to the hand from the cardstack
                                                                                if turntable.index(turn)==len(turntable)-1:
                                                                                        turn=turntable[0]
                                                                                else:
                                                                                        turn=turntable[turntable.index(turn)+1]
 
                                                                        elif foo==10: #Player dealt an "throw"
                                                                                barfoo=self.Hand.pop(self.Hand.index(foo)) #Remove the card from the players hand
                                                                                OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                MissingCards.extend(OutCardStack)
                                                                                OutCardStack=[]
                                                                                if len(self.Hand)<MinHand and len(CardStack)!=0:
                                                                                        self.Hand.append(CardStack.pop()) #Add a new card to the hand from the cardstack
 
                                                                        elif bar!=1 and foo>=bar:
                                                                                barfoo=self.Hand.pop(self.Hand.index(foo)) #Remove the card from the players hand
                                                                                OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                if len(self.Hand)<MinHand and len(CardStack)!=0:
                                                                                        self.Hand.append(CardStack.pop()) #Add a new card to the hand from the cardstack
 
                                                                                if turntable.index(turn)==len(turntable)-1:
                                                                                        turn=turntable[0]
                                                                                else:
                                                                                        turn=turntable[turntable.index(turn)+1]
                                                                        else:
                                                                                barfoo=self.Hand.pop(self.Hand.index(foo)) #Remove the card from the players hand
                                                                                OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                self.Hand.extend(OutCardStack) #Add aaaaall the cards from the Outcardstack to the players hand
                                                                                OutCardStack=[] #Empty the OCS
                                                                                if turntable.index(turn)==len(turntable)-1:
                                                                                        turn=turntable[0]
                                                                                else:
                                                                                        turn=turntable[turntable.index(turn)+1]
 
                                                                        ServerListener.broadcast("DEAL"+MsgSep+str(self.UID)+MsgSep+str(foo))
                                                                        print("Player: "+self.Uname+" dealt a "+str(foo))
                                                                else:
                                                                        print("Player: "+self.Uname+" trying to deal nonexsisting card "+str(foo))
                                                        else:
                                                                #_________________________________________________________________________________________________________________
                                                                #Self Shown Cards (DECK)
                                                                if len(self.ShownCards)!=0:
                                                                        if int(arg[0]) in self.ShownCards:
                                                                                foo=int(arg[0]) #Card being dealt
 
                                                                                if len(OutCardStack)!=0:
                                                                                        bar=OutCardStack[len(OutCardStack)-1] #Last card dealt
                                                                                else:
                                                                                        bar=0
 
                                                                                if foo==1: #Player dealt an ace
                                                                                        barfoo=self.ShownCards.pop(self.ShownCards.index(foo)) #Remove the card from the players ShownCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                elif foo==2: #Player dealt an "hold"
                                                                                        barfoo=self.ShownCards.pop(self.ShownCards.index(foo)) #Remove the card from the players ShownCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                elif foo==10: #Player dealt an "throw"
                                                                                        barfoo=self.ShownCards.pop(self.ShownCards.index(foo)) #Remove the card from the players ShownCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        MissingCards.extend(OutCardStack)
                                                                                        OutCardStack=[]
 
                                                                                elif bar!=1 and foo>=bar:
                                                                                        barfoo=self.ShownCards.pop(self.ShownCards.index(foo)) #Remove the card from the players ShownCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
                                                                                else:
                                                                                        barfoo=self.ShownCards.pop(self.ShownCards.index(foo)) #Remove the card from the players ShownCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        self.Hand.extend(OutCardStack) #Add aaaaall the cards from the Outcardstack to the players Hand
                                                                                        OutCardStack=[] #Empty the OCS
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                ServerListener.broadcast("DEAL"+MsgSep+str(self.UID)+MsgSep+str(foo))
                                                                                print("Player: "+self.Uname+" dealt a "+str(foo))
 
 
                                                                elif len(self.HiddenCards)!=0:
                                                                        #_____________________________________________________________________________________________________________
                                                                        #self Hidden Cards
                                                                        if int(arg[0]) in self.HiddenCardsHidden:
                                                                                foo=self.HiddenCards[int(arg[0])] #Card being dealt
 
                                                                                self.HiddenCardsHidden.pop(int(arg[0]))
 
                                                                                if len(OutCardStack)!=0:
                                                                                        bar=OutCardStack[len(OutCardStack)-1] #Last card dealt
                                                                                else:
                                                                                        bar=0
 
                                                                                if foo==1: #Player dealt an ace
                                                                                        barfoo=self.HiddenCards.pop(self.HiddenCards.index(foo)) #Remove the card from the players HiddenCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                elif foo==2: #Player dealt an "hold"
                                                                                        barfoo=self.HiddenCards.pop(self.HiddenCards.index(foo)) #Remove the card from the players HiddenCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                elif foo==10: #Player dealt an "throw"
                                                                                        barfoo=self.HiddenCards.pop(self.HiddenCards.index(foo)) #Remove the card from the players HiddenCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        MissingCards.extend(OutCardStack)
                                                                                        OutCardStack=[]
 
                                                                                elif bar!=1 and foo>=bar:
                                                                                        barfoo=self.HiddenCards.pop(self.HiddenCards.index(foo)) #Remove the card from the players HiddenCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
                                                                                else:
                                                                                        barfoo=self.HiddenCards.pop(self.HiddenCards.index(foo)) #Remove the card from the players HiddenCards
                                                                                        OutCardStack.append(barfoo) #Add the card to the Outcardstack
                                                                                        self.Hand.extend(OutCardStack) #Add aaaaall the cards from the Outcardstack to the players HiddenCards
                                                                                        OutCardStack=[] #Empty the OCS
                                                                                        if turntable.index(turn)==len(turntable)-1:
                                                                                                turn=turntable[0]
                                                                                        else:
                                                                                                turn=turntable[turntable.index(turn)+1]
 
                                                                                ServerListener.broadcast("DEAL"+MsgSep+str(self.UID)+MsgSep+str(foo))
                                                                                print("Player: "+self.Uname+" dealt a "+str(foo))
                                                                else:
                                                                        print("Player: "+self.Uname+" won!")
                                        else:
                                                print("UNDEFINED RESPONSE FROM UID"+str(self.UID)+": "+str(data))
 
                                        # if time.clock()>(self.clock+5):
                                        #       PingThread=Tempty()
                                        #       def PingThread.ping(self, UID):
                                        #               self.ptime=CThreads[UID].ping()
                                        #               if self.ptime==False:
                                        #                       print("Lost connection to UID "+str(UID))
                                        #                       CThreads[UID].alive=False
                                        #                       CThreads[UID].state="LOSTCONN"
                                        #                       ServerListener.UpdateCThreads()
                                        #       def PingThread.run(self):
                                        #               PingThread.ping(self.UID)
                                        #       PingThread.start()
                        except socket.error, e:
                                #Error=e
                                pass
                if self.alive==False:
                        ServerListener.UpdateCThreads()
                        pass
 
ServerListener=server()
ServerListener.start()
 
Malive=True
while Malive:
        ServerListener.UpdateCThreads()
        #_____________________________________________________________________________________________________________________
        #Commands
        try:
                ComPar=string.split(raw_input(">>"), " ")
                Command=ComPar[0]
               
                if Command=="ls":
                        print("UID TYPE      IP          PORT    STATE   TID")
                        for x in CThreads:
                                print (str(x)+" "*(3-len(str(x)))+":"+str(CThreads[x]))
 
                elif Command=="killinactive":
                        print("Killing inactive client threads")
                        ServerListener.UpdateCThreads()
 
                elif Command=="clist":
                        print("CLI:    Info:")
                        for x in ServerListener.CList:
                                print(ServerListener.CList[x])
               
                elif Command=="clistupd":
                        print("Updating Client List...")
                        ServerListener.UpdateCList()
 
                elif Command=="crashthread":
                        if ComPar[1]=="main":
                                crash=10+"Fuckthis"
                        elif ComPar[1]=="server":
                                ServerListener.Crash()
                        elif ComPar[1]=="nice":
                                Malive=False
 
                elif Command=="restart":
                        SetTitle("Shutting down...")
                        for x in CThreads:
                                print("Disconnecting Client: "+CThreads[x].getName())
                                CThreads[x].channel.close()
                                CThreads[x].alive=False
                        print("Killing server manager")
                        #ServerManager.alive=False
                        print("Killing server thread: "+ServerListener.getName())
                        ServerListener.alive=False
                        server_socket.close()
                        #Startup process
                        print("Booting up..")
                        Bootup()
                        print("ServerListener starting..")
                        ServerListener=server()
                        ServerListener.start()
                        Setup()
                        print("Reboot complete")
 
                elif Command=="send":
                        try:
                                if int(ComPar[1]) in CThreads:
                                        foo=""
                                        for x in ComPar:
                                                if not x=="send" and x!=ComPar[1]:
                                                        foo=foo+x+" "
                                        CThreads[int(ComPar[1])].send(foo)
                        except ValueError, e:
                                Error=e
                                print("send must be used with an userid")
 
                elif Command=="broadcast":
                        try:
                                foo=""
                                for x in ComPar:
                                        if not x=="broadcast":
                                                foo=foo+x+" "
                                ServerListener.broadcast(foo)
                        except ValueError, e:
                                Error=e
                                print("broadcast must be used with shit")
 
                elif Command=="ping":
                        try:
                                if int(ComPar[1]) in CThreads:
                                        print("Pinging: UID"+ComPar[1]+" | "+CThreads[int(ComPar[1])].getName())
                                        fooping=CThreads[int(ComPar[1])].ping()
                                        if fooping:
                                                print("Pinging successful, time taken: "+str(fooping))
                                        else:
                                                print("Client refused to respond to ping in time")
                                else:
                                        print("User ID: "+ComPar[1]+" does not exsist")
                        except ValueError, e:
                                Error=e
                                print("Ping must be used with an user id (UID)")
 
                elif Command=="exit":
                        SetTitle("Shutting down...")
                        for x in CThreads:
                                print("Disconnecting Client: "+CThreads[x].getName())
                                CThreads[x].channel.close()
                                CThreads[x].alive=False
                        print("Killing server manager")
                        #ServerManager.alive=False
                        print("Killing server thread: "+ServerListener.getName())
                        ServerListener.alive=False
                        server_socket.close()
                        print("Killing mainloop")
                        os.system("PAUSE")
                        Malive=False
 
                elif Command=="lasterror":
                        print(Error)
 
                elif Command=="berror":
                        print(BError)
               
                elif Command=="kick":
                        try:
                                if int(ComPar[1]) in CThreads:
                                        print("Kicking: UID"+ComPar[1]+" | "+CThreads[int(ComPar[1])].getName())
                                        reason=""
                                        for x in ComPar:
                                                if not (x=="kick" or x==str(ComPar[1])):
                                                        reason=reason+x+" "
                                        ServerListener.broadcast("KICK"+MsgSep+ComPar[1]+MsgSep+reason)
                                        CThreads[int(ComPar[1])].alive=False
                                        del CThreads[int(ComPar[1])]
                                        ServerListener.UpdateCList()
                                else:
                                        print("User ID: "+ComPar[1]+" does not exsist")
                        except ValueError, e:
                                Error=e
                                print("Kick must be used with an user id (UID)")
       
                elif Command=="say":
                        stri=""
                        for x in ComPar:
                                if not x=="say":
                                        stri=stri+x+" "
                        ServerListener.broadcastMSG("SERVER",0,stri)
 
                elif Command=="clear":
                        os.system("CLS")
 
                #______________________________________________________________________________________________________________________________________
                #Cardiac Spesific Commands:
                elif Command=="cardstack":
                        print(CardStack)
 
                elif Command=="outcards":
                        print(OutCardStack)
 
                elif Command=="missingcards":
                        print(MissingCards)
 
                elif Command=="cardstacks":
                        print("\nCardstack:")
                        print(CardStack)
                        print("\nOut Cards:")
                        print(OutCardStack)
                        print("\nMissingCards")
                        print(MissingCards)
 
                elif Command=="throwcards":
                        print("Throwing cards")
                        OutCardStack.extend(CardStack)
                        CardStack=[]
 
                elif Command=="cards":
                        print("User: "+str(CThreads[int(ComPar[1])].Uname+"'s cards"))
                        print("Hand: "+str(CThreads[int(ComPar[1])].Hand))
                        print("Deck: "+str(CThreads[int(ComPar[1])].ShownCards))
                        print("Hidden: "+str(CThreads[int(ComPar[1])].HiddenCards))
 
                elif Command=="Reshuffle":
                        Setup()
 
                elif Command=="":
                        #\Random scribble
                        #Once there comes a time.. Where you hear the certain call, and the wolves, come, together as one.
                        #/Random scribble
                        pass
 
                else:
                        #Lua Extension for commands here:
                        print("Command *"+Command+"* not found")
        except IndexError, e:
                print("Command *"+Command+"* requires "+str("N/A")+" arguments, "+str(len(ComPar)-1)+" given")
        except ValueError, e:
                print("An exception occured: ValueError. Probleary you typed a number where a text were required or the opposite. Type lasterror for more information")
                Error=e
        except TypeError, e:
                print("An exception occured: TypeError. Probleary you typed a number where a text were required or the opposite. Type lasterror for more information")
                Error=e
print("Mainloop ended")