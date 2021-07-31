from logging import exception
from tkinter.constants import DISABLED, END, GROOVE, LEFT, NSEW, RIGHT
from riotwatcher import LolWatcher, ApiError
from PIL import Image, ImageTk
import tkinter as tk
import tensorflow as tf
import time
from tensorflow import keras
import requests
import threading



class Application:
    #initialize
    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.onClose)
        master.title("A simple GUI")
        master.geometry("800x600")
        master.resizable(False, False)
        master.configure(background='#80b3ff')
        master.title("League Predictor")
        self.blueTeam = []
        self.redTeam = []
        self.blueTeamChamps = []
        self.redTeamChamps = []
        self.killAllThreads = False
        self.model = tf.keras.models.load_model('models/model1')
        self.setup()
    
    def setup(self):
        self.label = tk.Label(self.master, text="League of Legends Game Predictor", font=("Ariel", 24))
        self.label.configure(background='#80b3ff')
        self.label.pack()

        self.apiEntry = tk.Entry(self.master)
        self.apiEntry.place(x=300,y=50,width=300,height=20)

        self.greet_button = tk.Button(self.master, text="Enter API Key", command=self.startThread)
        self.greet_button.place(x=200,y=50,width=80,height=20)

        self.close_button = tk.Button(self.master, text="Close", command=self.onClose)
        self.close_button.place(x=350,y=550,width=100,height=40)

        self.close_button = tk.Button(self.master, text="Threads", command=self.checkThreads)
        self.close_button.place(x=150,y=550,width=100,height=40)



    def checkThreads(self):
        for thread in threading.enumerate(): 
            print(thread.name)
    
    def startThread(self):
        x = threading.Thread(target=self.getAPIKey)
        x.start()

    #create the names of players and their champion icons
    def createNamesAndIcons(self):
        self.entries=[]
        self.champImgs=[]

        #create winningTeam and percentages tab
        self.winningTeam = tk.Label(self.master, text="Winning Team: ", font=("Ariel", 18))
        self.winningTeam.configure(background='#80b3ff')
        self.winningTeam.pack(side='bottom', pady=70)

        self.blueConfidence = tk.Label(self.master, text="Blue Confidence: ", font=("Ariel", 18))
        self.blueConfidence.configure(background='#80b3ff')
        self.blueConfidence.place(x=20,y=500)

        self.redConfidence = tk.Label(self.master, text="Red Confidence: ", font=("Ariel", 18))
        self.redConfidence.configure(background='#80b3ff')
        self.redConfidence.place(x=530,y=500)

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
        print('resetting')

    
    def onClose(self):
        print("closed")
        self.killAllThreads = True
        self.master.destroy()

    def killThreads(self):
        if self.killAllThreads:
            print("Threads Killed")
            self.master.destroy()


    def getAPIKey(self):
        x1 = self.apiEntry.get()
        try:
            lol_watcher = LolWatcher(x1)
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

    def waitForActiveGame(self):
        while True:
            self.killThreads()
            try:
                response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
                print('used')
                for player in response['allPlayers']:
                    if player['team'] == 'ORDER':
                        self.blueTeam.append(player['summonerName'])
                        self.blueTeamChamps.append(player['rawChampionName'].replace('game_character_displayname_',''))
                    else:
                        self.redTeam.append(player['summonerName'])
                        self.redTeamChamps.append(player['rawChampionName'].replace('game_character_displayname_',''))

                print(self.blueTeam)
                print(self.redTeam)
                self.createNamesAndIcons()
                self.analyzeGame()
                break
            except Exception as e:
                print(e)
    
    
    def getTotalItemValue(self, player):
        totalGold = 0
        for i in player:
            itemID = str(i['itemID'])
            totalGold += self.items[itemID]['gold']['total']
        return totalGold
    
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
            self.killThreads()
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
                            if event['KillerName'] in self.blueTeam:
                                data[1] = 1
                            elif event['KillerName'] in self.redTeam:
                                data[1] = 2
                        elif event['EventName'] == "TurretKilled":
                            if event['KillerName'] in self.blueTeam:
                                data[6] += 1
                            elif event['KillerName'] in self.redTeam:
                                data[10] += 1
                        elif event['EventName'] == "InhibKilled":
                            if event['KillerName'] in self.blueTeam:
                                if not firstInhib:
                                    data[2] = 1
                                data[7] += 1
                            elif event['KillerName'] in self.redTeam:
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
                self.blueConfidence.configure(text="Blue Confidence: \n" + str(round(x[0][1]*100)))
                self.redConfidence.configure(text="Red Confidence: \n" + str(round(x[0][0]*100)))

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
my_gui = Application(root)
root.mainloop()
