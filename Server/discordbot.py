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

    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
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

    async def end(self, message):
        global client
        # サーバー起動のメッセージを削除する
        await self.msg.delete()
        self.vc = None
        self.msg = None

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
        print(vc)
        if self.vc:
            for member in self.vc.members:
                await member.edit(mute=True)
                await member.edit(deafen=True)

    async def help(self):
        pass

    # ゲーム開始時、ミーティング終了時に実行
    async def startTask(self):
        print("startTasks")
        pass

    # ミーティング開始時に実行
    async def startDiscussion(self):
        print("startDiscussion")
        pass

    # ロビーにプレイヤーが参加する都度実行
    async def startLobby(players):
        print("startLobby")
        undeafenAll()
        unmuteAll()
        # Msg部分を作成
        text = ""
        text += "ゲームステータス=ロビー\n"
        for player in players:
            text += player['name'] + "="
            for member in vc.members:
                if player['name'] == member.display_name:
                    text += "@" + member.display_name
            text += " " + int(player['colorId'])
            text += " " + int(player['isDead'])
            text += "\n"
        pass

    def __init__(self):
        self.client.run(TOKEN)

# ここからFlask用定義
app = Flask(__name__)
app.debug = True
@app.route('/mutebot', methods=['GET', 'POST'])
def receiveMsg():
    client = DiscordBot().client
    print("mutebot")
    if request.method == 'POST':
        data = request.json
        if data['GameStatus'] == EventId.Discussion:
            function = asyncio.run_coroutine_threadsafe(startDiscussion(data), client.loop)
            function.result()
        elif data['GameStatus'] == EventId.Lobby:
            function = asyncio.run_coroutine_threadsafe(startLobby(data), client.loop)
            function.result()
        elif data['GameStatus'] == EventId.Task:
            function = asyncio.run_coroutine_threadsafe(startTask(data), client.loop)
            function.result()
        elif data["GameStatus"] == EventId.Unknown:
            pass
        return Response("{'a':'b'}", status=201, mimetype='application/json')
    if request.method == 'GET':
        print('muteall')
        muteall = asyncio.run_coroutine_threadsafe(muteAll(), client.loop)
        muteall.result()
        return 'Hello, World!'

# main関数
def startWebServer():
    pass

def startDiscordBot():
    DiscordBot()

def main():
    thread1 = Thread(target=startDiscordBot)
    thread1.start()
    app.run('0.0.0.0', port=8080)
    thread1.join()

if __name__ == "__main__":
    main()