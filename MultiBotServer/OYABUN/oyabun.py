# coding: utf-8
from enum import Enum
import re
from multiprocessing import Process
import discord
from discord.ext import commands
from flask import Flask, render_template, request, redirect, url_for, Response
import os, sys
from threading import Thread
from singleton_decorator import singleton
import time
import asyncio
import json
import shlex
import socket
import argparse


# DiscordRateLimit回避用のBOT
SLAVES = []

class EventId(Enum):
    Lobby = 0
    Task = 1
    Discussion = 2
    UnKnown = 3

os.environ['FLASK_ENV'] = 'development'
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

# ここからDiscordBot用定義
Intents = discord.Intents.default()
Intents.members = True

if getattr(sys, 'frozen', False):
    baseDir = os.path.dirname(os.path.abspath(sys.executable))
else:
    baseDir = os.path.dirname(os.path.abspath(__file__))
# TOKENPATH = baseDir + "/TOKEN"
# if os.path.isfile(TOKENPATH):
#     with open(TOKENPATH) as f:
#         TOKEN = f.read()
# else:
#     TOKEN = os.getenv("DISCORD_TOKEN", default="")

parser = argparse.ArgumentParser()
parser.add_argument('--token', default='')
args = parser.parse_args()
TOKEN = args.token

def colorIdToName(colorId):
    return{
        0: "red",
        1: "blue",
        2: "green",
        3: "pink",
        4: "orange",
        5: "yellow",
        6: "black",
        7: "white",
        8: "purple",
        9: "brown",
        10: "cyan",
        11: "lime",
        12: "salmon",
        13: "bordeaux",
        14: "olive",
        15: "turqoise",
        16: "mint",
        17: "lavender",
        18: "nougat",
        19: "peach",
        20: "wasabi",
        21: "hotpink",
        22: "grey",
        23: "petrol",
    }.get(colorId)

def NameToColorId(name):
    return{
        "red": 0,
        "blue": 1,
        "green": 2,
        "pink": 3,
        "orange": 4,
        "yellow": 5,
        "black": 6,
        "white": 7,
        "purple": 8,
        "brown": 9,
         "cyan": 10,
         "lime": 11,
         "salmon": 12,
         "bordeaux": 13,
         "olive": 14,
         "turqoise": 15,
         "mint": 16,
         "lavender": 17,
         "nougat": 18,
         "peach": 19,
         "wasabi": 20,
         "hotpink": 21,
         "grey": 22,
         "petrol": 23,
    }.get(name)



@singleton
class DiscordBot:
    client = discord.Client(intents=Intents)
    vc = None
    msg = None
    nameConverter = {}
    colorConverter = {}
    players = []
    code = ""
    isRunning = False
    thumbnail = 'https://raw.githubusercontent.com/haoming37/MuteBot/master/SHHHHHHH.jpg'


    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        # 多重起動したのを検知するためのログ
        print('ログインしました')

    @client.event
    async def on_reaction_add(reaction, user):
        # リアクションをしたのがBOTじゃない場合のみ実施
        if reaction.message == DiscordBot().msg:
            if reaction.message.author != user:
                print(reaction.emoji)
                color = NameToColorId(re.sub(r"^au", "", reaction.emoji.name))

                # 他の色にリンクされている場合は外す
                for key in DiscordBot().colorConverter:
                    if key != str(color) and DiscordBot().colorConverter[key] == user.display_name:
                        DiscordBot().colorConverter[key] = ""
                # 既にリンクされている場合はリンクを外す
                if str(color) in DiscordBot().colorConverter and DiscordBot().colorConverter[str(color)] == user.display_name:
                    DiscordBot().colorConverter[str(color)] = ""
                else:
                    DiscordBot().colorConverter[str(color)] = user.display_name

                await DiscordBot().updateMessage(DiscordBot().players)
                await reaction.remove(user)
            

    @client.event
    async def on_message(message):
        content = message.content
        discordbot = DiscordBot()
        if re.match('^/msm [a-z].*$', content):
            command = shlex.split(content)[1]
            print(content)
            if command == "new" or command == "n":
                await discordbot.new(message)
            elif command == "end" or command == "e":
                await discordbot.end(message)
            elif command == "unmute" or command == "u":
                await discordbot.unmuteAll()
            elif command == "mute" or command == "u":
                await discordbot.muteAll()
            elif command == "list" or command == "l":
                await discordbot.linkList(message)
            elif command == "link":
                await discordbot.link(message)
            elif command == "list" or command == "l":
                await discordbot.linkList(message)
            elif command == "link":
                await discordbot.link(message)
            else:
                await discordbot.help(message)

    async def new(self, message):
        # メッセージ送り主のいるボイスチャンネルを探す
        vcs = message.guild.voice_channels
        author = message.author
        targetvc = None
        for v in vcs:
            if targetvc != None:
                break
            for member in v.members:
                if targetvc !=None:
                    break
                if member == author:
                    targetvc = v
                    break
        if targetvc == None:
            message.channel.send("ボイスチャンネルに参加してからコマンドを実行してください")
            return
        if os.path.isfile(baseDir + "/nameConverter.json"):
            with open(baseDir +"/nameConverter.json", "r") as f:
                self.nameConverter = json.load(f)
        if os.path.isfile(baseDir + "/colorConverter.json"):
            with open(baseDir +"/colorConverter.json", "r") as f:
                self.colorConverter = json.load(f)
        embed = discord.Embed(title="MuteBot接続待ち", description="クライアント接続待ち", color=0xff0000)
        embed.set_thumbnail(url=self.thumbnail)
        self.msg = await message.channel.send(embed=embed)
        self.vc = targetvc
        self.isRunning = True

    async def end(self, message):
        # ミュートを解除する
        await self.unmuteAll()
        # サーバー起動のメッセージを削除する
        if self.isRunning:
            await self.msg.delete()
            self.vc = None
            self.msg = None
            self.isRunning = False
            with open(baseDir +"/nameConverter.json", "w") as f:
                json.dump(self.nameConverter,f)
            with open(baseDir +"/colorConverter.json", "w") as f:
                json.dump(self.colorConverter,f)
        else:
            message.channel.send("MuteBotが起動していません")

    async def unmuteAll(self):
        # チャンネル内の全員のミュートステータスを解除する
        if self.vc:
            voicestatus = {}
            for member in self.vc.members:
                voicestatus[member.display_name] = {"mute": False, "deafen": False}
            await self.setVoiceStatus(voicestatus)

    async def muteAll(self):
        print('muteAll')
        if self.vc:
            voicestatus = {}
            for member in self.vc.members:
                voicestatus[member.display_name] = {"mute": True, "deafen": True}
            await self.setVoiceStatus(voicestatus)

    async def help(self, message):
        text = """
```使い方
/msm new
/msm end
/msm unmute
/msm link <AmongUsプレイヤー名> @<Discord表示名>
※リンク結果はロビーで色を変える、入り直す等をすると反映されます
```
        """
        await message.channel.send(text)

    # ゲーム開始時、ミーティング終了時に実行
    async def startTask(self, players):
        if self.msg == None:
            return
        print("startTasks")
        voicestatus = {}
        for player in players:
            convertedName = self._getConvertedName(player['name'], player['colorId'])
            for member in self.vc.members:
                if convertedName == member.display_name:
                    print("Match")
                    print(convertedName)
                    if player['isDead']:
                        voicestatus[member.display_name] = {'mute': False, 'deafen': False}
                    else:
                        voicestatus[member.display_name] = {'mute': True, 'deafen': True}
        await self.setVoiceStatus(voicestatus)
        await self.updateMessage(players)
    
    async def setVoiceStatus(self,voicestatus):
        global SLAVES
        print("setVoiceStatus")
        print(voicestatus)
        #　SLAVEがいる場合は分割する
        if len(SLAVES) >= 0:
            # ジョブを分割する
            print("子分と分割実行")
            num, rem = divmod(len(voicestatus), (len(SLAVES)+1))
            print(num)
            print(rem)
            master = num
            items = []
            item = {}
            counter = 0
            # num個をそれぞれに割り当てる、rem個を最終要素に挿入
            for index in voicestatus:
                item[index] = voicestatus[index]
                counter += 1
                if counter >= num and len(items) < (len(SLAVES) + 1) :
                    items.append(item)
                    item = {}
                    counter = 0
            if item != {}:
                items.append(item)
                item = {}

            # 割り切れなかった余りを上から一つずつ挿入
            if rem != 0:
                counter = 0
                print(len(items))
                print(len(SLAVES))
                if len(items) == len(SLAVES)+2:
                    for index in items[len(SLAVES)+1]:
                        items[counter][index] = items[len(SLAVES)+1][index]
                        counter += 1
                else:
                    print("子分の数よりもプレイヤーが少ない場合")

            # SLAVEに処理を実行させる
            for i in range(0, len(SLAVES)):
                print("子分が実行")
                if i >= len(items):
                    print("子分の数よりもプレイヤーが少ないためbreak")
                    break
                SLAVES[i].data = items[i]
                print(items[i])

            # Masterに処理を実行させる
            if len(items) >= len(SLAVES) + 1:
                voicestatus = items[len(SLAVES)]
                print("親分が実行")
                print(voicestatus)



        # MASTERで処理を実行
        try:
            cors = []
            for member in self.vc.members:
                name = member.display_name
                if name in voicestatus:
                    cors.append(self._setVoiceStatus(voicestatus, member, name, 'mute'))
                    cors.append(self._setVoiceStatus(voicestatus, member, name, 'deafen'))
            await asyncio.gather(*cors)
        except Exception as e:
            print(e)
    
    async def _setVoiceStatus(self, voicestatus, member, name, status):
        if status == 'mute':
            while voicestatus[name][status] != member.voice.mute:
                await member.edit(mute=voicestatus[name][status])
        elif status == 'deafen':
            while voicestatus[name][status] != member.voice.deaf:
                await member.edit(deafen=voicestatus[name][status])

    def _getConvertedName(self, name, colorId):
        convertedName = ""
        if str(colorId) in self.colorConverter:
            convertedName = self.colorConverter[str(colorId)]

        #elif name in self.nameConverter:
        #    convertedName = self.nameConverter[name]
        return convertedName

    # ミーティング開始時に実行
    async def startDiscussion(self, players):
        if self.msg == None:
            return
        print("startDiscussion")
        voicestatus = {}
        for player in players:
            flag = True
            convertedName = self._getConvertedName(player['name'], player['colorId'])
            for member in self.vc.members:
                if convertedName == member.display_name:
                    print("Match")
                    print(convertedName)
                    if player['isDead']:
                        voicestatus[convertedName] = {'mute': True, 'deafen': False}
                    else:
                        voicestatus[convertedName] = {'mute': False, 'deafen': False}
        await self.setVoiceStatus(voicestatus)
        await self.updateMessage(players)

    # ロビーにプレイヤーが参加する都度実行
    async def startLobby(self,players):
        if self.msg == None:
            return
        print("startLobby")
        self.players = players
        await self.unmuteAll()
        # Msg部分を作成
        await self.updateMessage(players)


    async def updateMessage(self, players):
        print(self.colorConverter)
        print("updateMessage")
        if self.msg == None:
            return
        text = ""
        emojis = []
        for player in players:
            emojiName  = "au" + colorIdToName(player['colorId'])
            emoji = discord.utils.get(self.msg.guild.emojis, name=emojiName)
            emojis.append(emoji)
            emojiText = "<:" + emoji.name + ":" + str(emoji.id) + ">"

            text += emojiText
            text += player['name'] + " <=> "

            convertedName = self._getConvertedName(player['name'], player['colorId'])
            flag = True
            for member in self.vc.members:
                if member.bot:
                    if convertedName == member.name:
                        text += "<@" + str(member.id) + ">"
                        flag = False
                else:
                    if convertedName == member.display_name:
                        text += "<@" + str(member.id) + ">"
                        flag = False
            if flag:
                text += "未接続です " + emojiText + "をクリック"
            text += "\n"
        embed = discord.Embed(title="ルームコード: " + self.code, description=text, color=0xff0000)
        embed.set_thumbnail(url=self.thumbnail)
        await self.msg.edit(embed=embed)


        reactions = discord.utils.get(self.client.cached_messages, id=self.msg.id).reactions
        reactions = reactions.copy()
        cors = []
        # Msgに不要なリアクションを削除する
        for reaction in reactions:
            flag = False
            for emoji in emojis:
                if reaction.emoji.id == emoji.id:
                    flag = True
                    break
            if not flag:
                print("remove", end='')
                print(reaction.emoji)
                cors.append(self.msg.remove_reaction(reaction.emoji,self.msg.author))

        # Msgに足りないリアクションを追加する
        for emoji in emojis:
            flag = False
            for reaction in reactions:
                if emoji.id == reaction.emoji.id:
                    flag = True
                    break
            if not flag:
                print("add", end='')
                print(emoji)
                cors.append(self.msg.add_reaction(emoji))
        await asyncio.gather(*cors)

class slave():
    thread = None
    data = {}
    asyncLock = asyncio.Lock()
    conn = None
    addr = None
    def run(self):
        print("run")
        try:
            with self.conn:
                while True:
                    data = self.conn.recv(1024)
                    if self.data != {}:
                        js = json.dumps(self.data)
                        js += "\0"
                        data = js.encode('utf-8')
                        self.data = {}
                    else:
                        data = "NONE\0".encode('utf-8')
                    self.conn.sendall(data)
        except Exception as e:
            print(e)
            SLAVES.remove(self)

    def __init__(self, conn, addr):
        print("Misimoの子分接続")
        self.conn = conn
        self.addr = addr
        self.thread = Thread(target=self.run)
        self.thread.start()

def socketServer():
    global SLAVES
    HOST = "127.0.0.1"
    PORT = 65340

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        # 接続待ち
        print("Misimoの子分接続待ち")
        s.listen(5)
        while True:
            # 接続許可
            conn, addr = s.accept()
            slv = slave(conn, addr)
            SLAVES.append(slv)
        s.close()

# ここからFlask用定義
app = Flask(__name__)
app.debug = True
@app.route('/mutebot', methods=['POST'])
def receiveMsg():
    db = DiscordBot()
    client = db.client
    print("mutebot")
    if request.method == 'POST':
        discordbot = DiscordBot()
        print(request.data)
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        if 'code' in data and 'gameStatus' in data and 'players' in data:
            discordbot.code = data['code']
            if discordbot.isRunning:
                if data['gameStatus'] == EventId.Discussion.value:
                    function = asyncio.run_coroutine_threadsafe(db.startDiscussion(data['players']), client.loop)
                    function.result()
                elif data['gameStatus'] == EventId.Lobby.value:
                    function = asyncio.run_coroutine_threadsafe(db.startLobby(data['players']), client.loop)
                    function.result()
                elif data['gameStatus'] == EventId.Task.value:
                    function = asyncio.run_coroutine_threadsafe(db.startTask(data['players']), client.loop)
                    function.result()
                elif data["gameStatus"] == EventId.Unknown.value:
                    pass
            return Response("{}", status=200, mimetype='application/json')
        else:
            return Response("{}", status=400, mimetype='application/json')


# main関数
def startDiscordBot():
    DiscordBot().client.run(TOKEN)

def main():
    thread1 = Thread(target=startDiscordBot)
    thread1.start()
    thread2 = Thread(target=socketServer)
    thread2.start()
    app.run('0.0.0.0', port=8080)
    thread1.join()

if __name__ == "__main__":
    main()