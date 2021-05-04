from enum import Enum
import re
from multiprocessing import Process
import discord
from flask import Flask, render_template, request, redirect, url_for, Response
import os
from threading import Thread
from singleton_decorator import singleton
import time
import asyncio
import json


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
baseDir =os.path.dirname(os.path.abspath(__file__))
TOKENPATH = baseDir + "/TOKEN"
if os.path.isfile(TOKENPATH):
    with open(TOKENPATH) as f:
        TOKEN = f.read()
else:
    TOKEN = os.getenv("DISCORD_TOKEN", default="")


@singleton
class DiscordBot:
    client = discord.Client(intents=Intents)
    vc = None
    msg = None
    nameConverter = {"Nearpie": "haoming"}
    isRunning = False

    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        # 多重起動したのを検知するためのログ
        print('ログインしました')

    @client.event
    async def on_message(message):
        content = message.content
        discordbot = DiscordBot()
        if re.match('^/msm [a-z]*$', content):
            command = content.split(" ")[1]
            print(command)
            print(content)
            if command == "new" or command == "n":
                await discordbot.new(message)
            elif command == "end" or command == "e":
                await discordbot.end()
            elif command == "unmute" or command == "u":
                await discordbot.unmute(message)
            else:
                await discordbot.help()

    async def new(self, message):
        # サーバー起動のメッセージを作成
        print(message.channel)
        self.msg = await message.channel.send("MuteBot開始\nクライアント待ち")
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
        self.vc = targetvc
        self.isRunning = True

    async def end(self, message):
        # ミュートを解除する
        await self.unmute()
        # サーバー起動のメッセージを削除する
        await self.msg.delete()
        self.vc = None
        self.msg = None
        self.isRunning = False

    async def unmute(self, message):
        vcs = message.guild.voice_channels
        author = message.author
        targetvc = None
        for vc in vcs:
            if targetvc != None:
                break
            for member in vc.members:
                if targetvc !=None:
                    break
                if member == author:
                    targetvc = vc
                    break
        vc = targetvc
        for member in vc.members:
            await member.edit(mute=False)
            await member.edit(deafen=False)

    async def unmuteAll(self):
        # チャンネル内の全員のマイクミュートステータスを解除する
        if self.vc:
            for member in self.vc.members:
                await member.edit(mute=False)

    async def undeafenAll(self):
        # チャンネル内の全員のスピーカーミュートステータスを解除する
        if self.vc:
            for member in self.vc.members:
                await member.edit(deafen=False)

    async def muteAll(self):
        print('muteAll')
        if self.vc:
            for member in self.vc.members:
                await member.edit(mute=True)
                await member.edit(deafen=True)

    async def help(self):
        pass

    # ゲーム開始時、ミーティング終了時に実行
    async def startTask(self, players):
        if self.msg == None:
            return
        print("startTasks")
        for player in players:
            flag = True
            target = None
            if player['name'] in self.nameConverter:
                convertedName = self.nameConverter[player['name']]
                for member in self.vc.members:
                    if convertedName == member.display_name or player['name']== member.display_name:
                        target = member
                        flag = False
            if target:
                if player['isDead']:
                    await target.edit(mute=False)
                    await target.edit(deafen=False)
                else:
                    await target.edit(mute=True)
                    await target.edit(deafen=True)
        await self.updateMessage(players)

    # ミーティング開始時に実行
    async def startDiscussion(self, players):
        if self.msg == None:
            return
        print("startDiscussion")
        for player in players:
            flag = True
            target = None
            if player['name'] in self.nameConverter:
                convertedName = self.nameConverter[player['name']]
                for member in self.vc.members:
                    if convertedName == member.display_name or player['name']== member.display_name:
                        target = member
                        flag = False
            if target:
                if player['isDead']:
                    await target.edit(mute=True)
                    await target.edit(deafen=False)
                else:
                    await target.edit(mute=False)
                    await target.edit(deafen=False)
        await self.updateMessage(players)

    # ロビーにプレイヤーが参加する都度実行
    async def startLobby(self,players):
        if self.msg == None:
            return
        print("startLobby")
        await self.undeafenAll()
        await self.unmuteAll()
        # Msg部分を作成
        await self.updateMessage(players)


    async def updateMessage(self, players):
        if self.msg == None:
            return
        text = ""
        text += "MuteBot動作中\n"
        for player in players:
            text += player['name'] + "="

            if player['name'] in self.nameConverter:
                convertedName = self.nameConverter[player['name']]
            else:
                convertedName = ""
            for member in self.vc.members:
                if convertedName == member.display_name or player['name'] == member.display_name:
                    text += "<@" + str(member.id) + ">"
                    flag = False
                else:
                    text += "None"
            text += " colorId=" + str(player['colorId'])
            text += " " + str(player['isDead'])
            text += "\n"
        await self.msg.edit(content=text)


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
        return Response("{'a':'b'}", status=201, mimetype='application/json')
    if request.method == 'GET':
        if discordbot.isRunning:
            print('muteall')
            discordbot = DiscordBot()
            muteall = asyncio.run_coroutine_threadsafe(discordbot.muteAll(), client.loop)
            muteall.result()
        return 'Hello, World!'

# main関数
def startWebServer():
    pass

def startDiscordBot():
    DiscordBot().client.run(TOKEN)

def main():
    thread1 = Thread(target=startDiscordBot)
    thread1.start()
    app.run('0.0.0.0', port=8080)
    thread1.join()

if __name__ == "__main__":
    main()