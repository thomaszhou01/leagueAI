from tkinter.constants import ACTIVE, DISABLED, END, GROOVE, LEFT, NSEW, RIGHT, TOP
from riotwatcher import LolWatcher, ApiError
from PIL import Image, ImageTk
from tensorflow import keras
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import tkinter as tk
import time
import requests
import threading
import queue
import numpy as np



class LeagueAI:
    #initialize
    LIGHT_BLUE = '#80b3ff'
    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.onClose)
        master.title("A simple GUI")
        master.geometry("800x600")
        master.resizable(False, False)
        master.configure(background='#80b3ff')
        master.title("League Predictor")
        self.thread_queue = queue.Queue()
        self.blueTeam = []
        self.redTeam = []
        self.blueTeamChamps = []
        self.redTeamChamps = []
        self.goldDiff = []
        self.prediction = []
        self.gametime = []
        self.killAllThreads = False
        self.model = keras.models.load_model('models/modelHDF5.h5')
        self.setup()
        self.listen_for_result()
    
    def setup(self):
        self.label = tk.Label(self.master, text="League of Legends Game Predictor", font=("Ariel", 24))
        self.label.configure(background='#80b3ff')
        self.label.pack()

        self.connectionStatus = tk.Label(self.master, text="Connection Status:", font=("Ariel", 20))
        self.connectionStatus.configure(background='#80b3ff')
        self.connectionStatus.pack(side=TOP, pady=50)

        self.apiStart = tk.Button(self.master, text="Connect To Game", command=self.startThread)
        self.apiStart.place(x=325,y=50,width=150,height=40)

        self.close_button = tk.Button(self.master, text="Close", command=self.onClose)
        self.close_button.place(x=350,y=550,width=100,height=40)

        self.threadsButton = tk.Button(self.master, text="Threads", command=self.createGraph)
        self.threadsButton.place(x=150,y=550,width=100,height=40)

    #test
    def listen_for_result(self):
        """ Check if there is something in the queue. """
        try:
            self.res = self.thread_queue.get(0)
            self._print(self.res)
        except queue.Empty:
            self.master.after(100, self.listen_for_result)

    def checkThreads(self):
        for thread in threading.enumerate(): 
            print(thread.name)
        print(self.gametime)
        print(self.goldDiff)
        print(len(self.gametime))
        print(len(self.goldDiff))

    
    def startThread(self):
        try:
            self.canvas.get_tk_widget().destroy()
            self.canvas2.get_tk_widget().destroy()
        except:
            pass
        self.goldDiff.clear()
        self.gametime.clear()
        self.prediction.clear()
        self.apiStart.configure(state=DISABLED)
        self.secondThread = threading.Thread(target=self.getAPIKey)
        self.secondThread.daemon = True
        self.secondThread.start()

    def onClose(self):
        print("closed")
        self.master.destroy()
    
    def displayConnectionStatus(self, y):
        displayText = ""
        if "api_key or kernel_url" in y:
            displayText = "Connection Status:\nEnter API Key"
        elif "403 Client Error" in y:
            displayText = "Connection Status:\nInvalid API Key"
        elif "HTTPSConnectionPool(host=" in y:
            displayText = "Connection Status:\nWaiting for Game"
        self.connectionStatus.configure(text=displayText)
        return y

    #create the names of players and their champion icons
    def createNamesAndIcons(self):
        self.entries=[]
        self.champImgs=[]
        self.connectionStatus.config(text="")

        #create winningTeam and percentages tab
        self.winningTeam = tk.Label(self.master, text="Winning Team: ", font=("Ariel", 18))
        self.winningTeam.configure(background='#80b3ff')
        self.winningTeam.pack(side='bottom', pady=70)

        self.blueConfidence = tk.Label(self.master, text="Blue Confidence: ", font=("Ariel", 18))
        self.blueConfidence.configure(background='#80b3ff')
        self.blueConfidence.place(x=20,y=500)

        self.redConfidence = tk.Label(self.master, text="Red Confidence: ", font=("Ariel", 18))
        self.redConfidence.configure(background='#80b3ff')
        self.redConfidence.place(x=600,y=500)

        self.blueTag = tk.Label(self.master, text="Blue Stats", font=("Ariel", 16))
        self.blueTag.configure(background='#80b3ff')
        self.blueTag.place(x=10,y=100)

        self.redTag = tk.Label(self.master, text="Red Stats", font=("Ariel", 16))
        self.redTag.configure(background='#80b3ff')
        self.redTag.place(x=680,y=100)

        self.blueKills = tk.Label(self.master, text="Kills: ", font=("Ariel", 12))
        self.blueKills.configure(background='#80b3ff')
        self.blueKills.place(x=10,y=150)

        self.redKills = tk.Label(self.master, text="Kills: ", font=("Ariel", 12))
        self.redKills.configure(background='#80b3ff')
        self.redKills.place(x=680,y=150)

        self.blueTowers = tk.Label(self.master, text="Towers: ", font=("Ariel", 12))
        self.blueTowers.configure(background='#80b3ff')
        self.blueTowers.place(x=10,y=200)

        self.redTowers = tk.Label(self.master, text="Towers : ", font=("Ariel", 12))
        self.redTowers.configure(background='#80b3ff')
        self.redTowers.place(x=680,y=200)

        self.blueInhibs = tk.Label(self.master, text="Inhibs: ", font=("Ariel", 12))
        self.blueInhibs.configure(background='#80b3ff')
        self.blueInhibs.place(x=10,y=250)

        self.redInhibs = tk.Label(self.master, text="Inhibs: ", font=("Ariel", 12))
        self.redInhibs.configure(background='#80b3ff')
        self.redInhibs.place(x=680,y=250)

        self.blueDragons = tk.Label(self.master, text="Dragons: ", font=("Ariel", 12))
        self.blueDragons.configure(background='#80b3ff')
        self.blueDragons.place(x=10,y=300)

        self.redDragons = tk.Label(self.master, text="Dragons: ", font=("Ariel", 12))
        self.redDragons.configure(background='#80b3ff')
        self.redDragons.place(x=680,y=300)

        self.blueBarons = tk.Label(self.master, text="Barons: ", font=("Ariel", 12))
        self.blueBarons.configure(background='#80b3ff')
        self.blueBarons.place(x=10,y=350)

        self.redBarons = tk.Label(self.master, text="Barons: ", font=("Ariel", 12))
        self.redBarons.configure(background='#80b3ff')
        self.redBarons.place(x=680,y=350)

        self.blueItems = tk.Label(self.master, text="Item Gold: ", font=("Ariel", 12))
        self.blueItems.configure(background='#80b3ff')
        self.blueItems.place(x=10,y=400)

        self.redItems = tk.Label(self.master, text="Item Gold: ", font=("Ariel", 12))
        self.redItems.configure(background='#80b3ff')
        self.redItems.place(x=680,y=400)

        #create labels and icons
        for i in range(len(self.blueTeam)):
            temp = []
            temp2 = []
            for j in range(2):
                #create labels
                x = tk.Entry(self.master, width=5, font=('Arial',16))
                x.place(x=200+200*j,y=100+75*i,width=200,height=75)
                x.insert(END, self.blueTeam[i] if j==0 else self.redTeam[i])
                x.configure(background='#80b3ff')
                temp.append(x)

                #create champion icons
                im = ImageTk.PhotoImage(Image.open(requests.get('https://ddragon.leagueoflegends.com/cdn/11.15.1/img/champion/'+(str(self.blueTeamChamps[i]) if j==0 else str(self.redTeamChamps[i]))+'.png', stream=True).raw).resize((75,75), Image.ANTIALIAS))
                y = tk.Label(image=im)
                y.image = im
                y.place(x=120 if j == 0 else 600, y=100+75*i)
                temp2.append(y)

            #store references 
            self.entries.append(temp)
            self.champImgs.append(temp2)
    
    
    def createGraph(self):
        # t = np.arange(0, 3, .01)
        # sin = np.sin(2 * np.pi * t)
        figure = Figure(figsize=(5, 4), dpi=100)
        figure.patch.set_facecolor('#80b3ff')
        subplot = figure.add_subplot(1,1,1)
        subplot.set_title("Item Value Difference")
        subplot.grid(True)
        subplot.plot(self.gametime, self.goldDiff)

        figure1 = Figure(figsize=(5, 4), dpi=100)
        figure1.patch.set_facecolor('#80b3ff')
        subplot1 = figure1.add_subplot(1,1,1)
        subplot1.set_title("Prediction (1 = Blue, 0 = Red)")
        subplot1.grid(True)
        subplot1.plot(self.gametime, self.prediction)

        self.canvas = FigureCanvasTkAgg(figure, master=root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x=50,y=100,width=700,height=200)
        
        self.canvas2 = FigureCanvasTkAgg(figure1, master=root)  # A tk.DrawingArea.
        self.canvas2.draw()
        self.canvas2.get_tk_widget().place(x=50,y=300,width=700,height=200)
        
    
    #works
    def resetWindow(self):
        for i in range(len(self.blueTeam)):
            for j in range(2):
                self.entries[i][j].destroy()
                self.champImgs[i][j].destroy()
        self.winningTeam.destroy()
        self.blueConfidence.destroy()
        self.redConfidence.destroy()
        self.blueTeam.clear()
        self.redTeam.clear()
        self.blueTeamChamps.clear()
        self.redTeamChamps.clear()
        self.blueTag.destroy()
        self.redTag.destroy()
        self.blueKills.destroy()
        self.redKills.destroy()
        self.blueTowers.destroy()
        self.redTowers.destroy()
        self.blueInhibs.destroy()
        self.redInhibs.destroy()
        self.blueDragons.destroy()
        self.redDragons.destroy()
        self.blueBarons.destroy()
        self.redBarons.destroy()
        self.blueItems.destroy()
        self.redItems.destroy()
        self.apiStart.configure(state=ACTIVE)

        self.connectionStatus.configure(text="Connection Status:")
        self.createGraph()
        print('resetting')


    def getAPIKey(self):
        try:
            lol_watcher = LolWatcher('')
            my_region = 'na1'
            versions = lol_watcher.data_dragon.versions_for_region(my_region)
            champions_version = versions['n']['champion']
            items_version=versions['n']['item']
            self.champions = lol_watcher.data_dragon.champions(champions_version)['data']
            self.items = lol_watcher.data_dragon.items(items_version)['data']
            self.me = lol_watcher.summoner.by_name(my_region, 'tomtom2352')
            self.waitForActiveGame()
        except Exception as e:
            print(e)
            self.apiStart.configure(state=ACTIVE)
            print("in getAPIKey")
            self.displayConnectionStatus(str(e))

    def waitForActiveGame(self):
        while True:
            try:
                response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
                print('used')
                for player in response['allPlayers']:
                    champion = player['rawChampionName'].replace('game_character_displayname_','')
                    if champion == "FiddleSticks":
                        champion = "Fiddlesticks"
                    if player['team'] == 'ORDER':
                        self.blueTeam.append(player['summonerName'])
                        self.blueTeamChamps.append(champion)
                    else:
                        self.redTeam.append(player['summonerName'])
                        self.redTeamChamps.append(champion)

                print(self.blueTeam)
                print(self.blueTeamChamps)
                print(self.redTeam)
                print(self.redTeamChamps)
                self.createNamesAndIcons()
                self.analyzeGame()
                break
            except Exception as e:
                print(e)
                print("in waitforActiveGame")
                self.displayConnectionStatus(str(e))
    
    
    def getTotalItemValue(self, player):
        totalGold = 0
        for i in player:
            itemID = str(i['itemID'])
            totalGold += self.items[itemID]['gold']['total']
        return totalGold
    
    #calculates in game stats
    def analyzeGame(self):
        listSize = 0
        data = [0]*16
        firstInhib = False
        firstBaron = False
        firstDragon = False
        firstHerald = False
        blueKills = 0
        redKills = 0
        
        
        
        while True:
            try:
                time.sleep(1)
                response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
                blueSpentGold = 0
                redSpentGold = 0
                #calculate item value
                for player in response['allPlayers']:
                    if player['summonerName'] in self.blueTeam:
                        blueSpentGold += self.getTotalItemValue(player['items'])
                    elif player['summonerName'] in self.redTeam:
                        redSpentGold += self.getTotalItemValue(player['items'])
                data[14] = blueSpentGold-redSpentGold
                if len(response['events']['Events']) > listSize: 
                    #calculate events
                    for event in response['events']['Events'][listSize:]:
                        if event['EventName'] == "FirstBlood":
                            if event['Recipient'] in self.blueTeam:
                                data[0] = 1
                            elif event['Recipient'] in self.redTeam:
                                data[0] = 2
                        elif event['EventName'] == "FirstBrick":
                            if event['KillerName'] in self.blueTeam or "Minion_T100" in event['KillerName']:
                                data[1] = 1
                            elif event['KillerName'] in self.redTeam or "Minion_T200" in event['KillerName']:
                                data[1] = 2
                        elif event['EventName'] == "TurretKilled":
                            if event['KillerName'] in self.blueTeam or "Minion_T100" in event['KillerName']:
                                data[6] += 1
                            elif event['KillerName'] in self.redTeam or "Minion_T200" in event['KillerName']:
                                data[10] += 1
                        elif event['EventName'] == "InhibKilled":
                            if event['KillerName'] in self.blueTeam or "Minion_T100" in event['KillerName']:
                                if not firstInhib:
                                    data[2] = 1
                                data[7] += 1
                            elif event['KillerName'] in self.redTeam or "Minion_T200" in event['KillerName']:
                                if not firstInhib:
                                    data[2] = 2
                                data[11] += 1
                        elif event['EventName'] == "BaronKill":
                            if event['KillerName'] in self.blueTeam:
                                if not firstBaron:
                                    data[3] = 1
                                data[8] += 1
                            elif event['KillerName'] in self.redTeam:
                                if not firstBaron:
                                    data[3] = 2
                                data[12] += 1
                        elif event['EventName'] == "DragonKill":
                            if event['KillerName'] in self.blueTeam:
                                if not firstDragon:
                                    data[4] = 1
                                data[9] += 1
                            elif event['KillerName'] in self.redTeam:
                                if not firstDragon:
                                    data[4] = 2
                                data[13] += 1
                        elif event['EventName'] == "HeraldKill":
                            if event['KillerName'] in self.blueTeam:
                                if not firstHerald:
                                    data[5] = 1
                            elif event['KillerName'] in self.redTeam:
                                if not firstHerald:
                                    data[5] = 2
                        elif event['EventName'] == "ChampionKill":
                            if event['KillerName'] in self.blueTeam:
                                blueKills += 1
                            elif event['KillerName'] in self.redTeam:
                                redKills += 1
                            data[15] = blueKills-redKills
                listSize = len(response['events']['Events'])
                x = self.model.predict([data])
                print(data)
                print(x)

                #Show the stats
                self.blueKills.configure(text="Kills: " + str(blueKills))
                self.redKills.configure(text="Kills: " + str(redKills))
                self.blueTowers.configure(text="Towers: " + str(data[6]))
                self.redTowers.configure(text="Towers: " + str(data[10]))
                self.blueInhibs.configure(text="Inhibs: " + str(data[7]))
                self.redInhibs.configure(text="Inhibs: " + str(data[11]))
                self.blueDragons.configure(text="Dragons: " + str(data[9]))
                self.redDragons.configure(text="Dragons: " + str(data[13]))
                self.blueBarons.configure(text="Barons: " + str(data[8]))
                self.redBarons.configure(text="Barons: " + str(data[12]))
                self.blueItems.configure(text="Item Gold: \n" + str(blueSpentGold))
                self.redItems.configure(text="Item Gold: \n" + str(redSpentGold))

                self.blueConfidence.configure(text="Blue Confidence: \n" + str(round(x[0][1]*100))+"%")
                self.redConfidence.configure(text="Red Confidence: \n" + str(round(x[0][0]*100))+"%")

                self.gametime.append(response['gameData']['gameTime']/60)
                self.goldDiff.append(blueSpentGold-redSpentGold)
                self.prediction.append(x[0][1])
                if x[0][0] > x[0][1]:
                    print("Red Advantage")
                    self.winningTeam.configure(text="Winning Team: Red")
                else:
                    print("Blue Advantage")
                    self.winningTeam.configure(text="Winning Team: Blue")
                    


            except Exception as e:
                print(e)
                self.resetWindow()
                break

root = tk.Tk()
gui = LeagueAI(root)
root.mainloop()
