from enum import Enum
import re
from multiprocessing import Process
import discord
from flask import Flask, render_template, request, redirect, url_for
import os

Intents = discord.Intents.default()
Intents.members = True

class DiscordBot:
    __instance = None
    TOKEN = ""
    client = discord.Client(intents=Intents)
    dcUsers = []
    auUsers = {} # キー = ゲーム内名、バリュー = Discrodユーザー
    vc = None
    msg = None

    def getInstance():
        if DiscordBot.__instance == None:
            DiscordBot()
        return DiscordBot.__instance

    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')

    @client.event
    async def on_message(message):
        content = message.content
        webserver = WebServer.getInstance()
        discordbot = DiscordBot.getInstance()
        if re.match('^/msm [a-z]*$', content):
            command = content.split(" ")[1]
            print(command)
            print(content)
            if command == "new" or command == "n":
                await discordbot.new(message)
            elif command == "end" or command == "e":
                await discordbot.end()
            elif command == "unmute" or command == "u":
                await discordbot.unmuteAll()
                await discordbot.undeafenAll()
            else:
                await discordbot.help()

            # コマンドを実行後に元のメッセージを削除する
            # await message.delete()
            # print("delete OK")

    async def new(self,message):
        # サーバー起動のメッセージを作成
        print(message.channel)
        self.msg = await message.channel.send("MuteBot開始\nクライアント待ち")
        # メッセージ送り主のいるボイスチャンネルを探す
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
        self.vc = targetvc
        # プラグインからゲームステータスを受け取るサーバーを起動する
        webserver = WebServer.getInstance()
        if webserver.isRunning:
            webserver.stopFalsk()
        webserver.startFlask()

    async def end(self):
        # サーバー起動のメッセージを削除する
        await self.msg.delete()
        self.vc = None
        self.dcUsers = []
        self.auUsers = {}
        # プラグインからゲームステータスを受け取るサーバーを終了する
        webserver = WebServer.getInstance()
        if webserver.isRunning:
            webserver.stopFlask()

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

    async def help(self):
        pass

    # ゲーム開始時、ミーティング終了時に実行
    async def startTasks(self):
        print("startTasks")
        pass
    
    # ミーティング開始時に実行
    async def startDiscussion(self):
        print("startDiscussion")
        pass

    # ロビーにプレイヤーが参加する都度実行
    async def startLobby(self, players):
        print("startLobby")
        self.undeafenAll()
        self.unmuteAll()
        # Msg部分を作成
        text = ""
        text += "ゲームステータス=ロビー\n"
        for player in players:
            text += player['name'] + "="
            for member in self.vc.members:
                if player['name'] = member.display_name:
                    text += "@" + member.display_name
            text += " " + int(player['colorId'])
            text += " " + int(player['isDead'])
            text += "\n"
        pass

    def __init__(self,TOKEN):
        if DiscordBot.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.TOKEN = TOKEN
            DiscordBot.__instance = self
            self.client.run(self.TOKEN)
        


# WebServerクラス
class EventId(Enum):
    StartLobby = 0
    StartTask = 1
    StartDiscussion = 2

class WebServer:
    # メンバー変数
    __instance = None
    isRunning = False
    app = Flask(__name__)
    app.debug = True
    server= None

    def getInstance():
        if WebServer.__instance == None:
            WebServer()
        return WebServer.__instance

    def __init__(self):
        if WebServer.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.server = Process(target=self.runFlaskProcess)
            WebServer.__instance = self

    def runFlaskProcess(self):
        self.app.run(host="0.0.0.0", port=8080)

    def startFlask(self):
        if self.server != None:
            self.server.start()
            self.isFlaskRunnin = True

    def stopFlask(self):
        if self.server != None and self.isRunning:
            self.server.terminate()
            self.server.join()
        self.isRunnig = False

    @app.route('/mutebot', methods=['GET,POST'])
    def receiveMsg():
        discordBot = DiscordBot.getInstance()
        if request.method == 'POST':
            data = request.json
            if data['eventid'] == EventId.StartDiscussion:
                discordBot.startDiscussion()
            elif data['eventid'] == EventId.StartLobby:
                discordBot.StartLobby()
            elif data['eventid'] == EventId.StartTask:
                discordBot.StartTask()

# main関数
def main():
    if os.path.isfile("TOKEN"):
        with open("TOKEN") as f:
            token = f.read()
    else:
        token = os.getenv("DISCORD_TOKEN", default="")
    WebServer()
    DiscordBot(token)

if __name__ == "__main__":
    main()