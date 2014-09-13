# -*- coding: utf-8 -*-
#Python Server DGram
#Cardgame server, by Anderen2
from __future__ import division #Python has an error when its dividing with numbers with decimals, like 1.23 and 2.02. 2.9/4.8=2 without this
from threading import Thread #Fra modulen threading, importer bare delen eller funksjonen Thread.
import socket, os, time, string
import random, pickle
 
def Setup():
        global CardStack, TotHiddenCards, TotShownCards, TotDealedHand, MinHand, TotCards, TotDiff, TotPer, DiffCards, OutCardStack, MissingCards, stage, turn
        #Sett spillregler
        TotHiddenCards=3
        TotShownCards=3
        TotDealedHand=3
        MinHand=3
 
        #Sett generelle regler
        stage=0
        turn=0
 
        #Generer og sett verdier for kortstokken
        TotCards=52 #Total mengde kort
        TotDiff=TotCards/4 #Total mengde forskjellige kort
        TotPer=TotCards/TotDiff #Total mengde av hvert enkelt kort
        DiffCards=[1,2,3,4,5,6,7,8,9,10,11,12,13] #De forskjellige kortene
        CardStack=[] #Kortstokken
        OutCardStack=[] #Utdelte kort
        MissingCards=[] #Utslåtte kort
        foo=0
        bar=0 #Midlertidige verdier
 
        #Loop for å lage en kortstokk med 4 av hvert kort (Kunne ha lagt kortstokken manuelt, men er lat)
        while foo!=TotDiff:
                foo=foo+1 #foo=foo+1
                while bar!=TotPer:
                        CardStack.append(foo) #Legg til kort i kortstokken
                        bar=bar+1
                bar=0
 
        #Bland kortene:
        random.shuffle(CardStack)
 
Setup()
 
#___________________________________________________________________________________________________________________________________
#Shameless copypaste from ServerThreaded.py
Conn=0
CThreads={}
PStatus=""
Error=""
BError=""
MsgSep="z_*"
 
ip="localhost"
port=2726
 
def SetTitle(Status=PStatus):
        global PStatus
        if Status!="":
                PStatus=Status
        os.system("title "+PStatus+" "+str(Conn)+"Conn")
 
server_socket=None
def Bootup():
        global server_socket
        SetTitle("Starting up...")
        server_socket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind ( ( ip, port ) )
        server_socket.settimeout(1)
        server_socket.listen(5)
        SetTitle("Listening...")
 
Bootup()
 
#________________________________________________________________________________________________________________
#SERVERTHREAD: UID 0
class server(Thread):
        def __init__(self, ip=ip, port=port):
                Thread.__init__(self)
                self.setName(ip+":"+str(port))
                self.alive=True
                self.CList={}
                self.CTLock=False
 
        def broadcast(self, Str):
                for x in CThreads:
                        CThreads[x].send(Str)
 
        def broadcastMSG(self, From, UID, Mesg):
                for x in CThreads:
                        if not str(x)==str(UID):
                                CThreads[x].MESG(str(UID),Mesg)
 
        def UpdateCList(self):
                self.CList={}
                for x in CThreads:
                        self.CList[x]={}
                        self.CList[x]["UID"]=CThreads[x].UID
                        self.CList[x]["Uname"]=CThreads[x].Uname
 
        def UpdateCThreads(self):
                if self.CTLock==False:
                        self.CTLock=True
                        DeadThreads={}
                        for x in CThreads:
                                if not CThreads[x].isAlive():
                                        DeadThreads[x]=CThreads[x]
                                        print("Removing dead thread: "+str(x))
                                        self.broadcast("DCONN"+MsgSep+str(CThreads[x].UID)+MsgSep+CThreads[x].state)
                        for x in DeadThreads:
                                del CThreads[x]
                        self.UpdateCList()
                        self.CTLock=False
 
        def run(self):
                global Conn, CThreads, Error
                print(self)
                while self.alive:
                        try:
                                SetTitle("Accepting Connections...")
                                channel, details = server_socket.accept()
                                print 'We have opened a connection with', details
                                Conn+=1
                                CThreads[Conn]=client(channel,Conn)
                                CThreads[Conn].state="Starting"
                                CThreads[Conn].start()
                                CThreads[Conn].setName(details)
                                self.UpdateCThreads()
                                self.broadcast("CONN"+MsgSep+str(Conn))
                                if self.alive==False:
                                        print("I should be dead.. :(")
 
                        except socket.timeout:
                                pass
 
                        except socket.error, e:
                                SError=e
                                print(e)
                                self.alive=False
                if self.alive==False:
                        print("Server stopped..")
 