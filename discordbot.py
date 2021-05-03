from enum import Enum
import re
from multiprocessing import Process
import discord
from flask import Flask, render_template, request, redirect, url_for

class DiscordBot:
    __instance = None
    TOKEN = "Nzg1MTEyMjcwNDAwNTIwMjEz.X8zGxw.yDAbDW66cvQB_BsIrksWyuPbVQU"
    client = discord.Client()

    def getInstance():
        if DiscordBot.__instance == None:
            DiscordBot()
        return DiscordBot.__instance

    def __init__(self):
        if DiscordBot.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.server = Process(target=self.runFlaskProcess)
            DiscordBot.__instance = self

    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')
    @client.event
    async def on_message(message):
        content = message.content
        webserver = WebServer.getInstance()
        if re.match('^/msm [a-z]*$', content):
            command = content.split(" ")[1]
            print(command)
            print(content)
            if command == "new" or command == "n":
                # プラグインからゲームステータスを受け取るサーバーを起動する
                if webserver.isRunning:
                    webserver.stopFalsk()
                webserver.startFlask()
            elif command == "end" or command == "e":
                # プラグインからゲームステータスを受け取るサーバーを終了する
                if webserver.isRunning:
                    webserver.stopFlask()
            elif command == "unmute" or command == "u":
                # チャンネル内の全員のミュートステータスを解除する
                pass
            else:
                # コマンドのhelpを投稿
                pass
            # コマンドを実行後に元のメッセージを削除する

    # ゲーム開始時、ミーティング終了時に実行
    def startTasks():
        print("startTasks")
        pass
    
    # ミーティング開始時に実行
    def startDiscussion():
        print("startDiscussion")
        pass

    # ロビーにプレイヤーが参加する都度実行
    def startLobby():
        print("startMeeting")
        pass

    def __init__(self):
        if WebServer.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.client.run(self.TOKEN)
            WebServer.__instance = self
        


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
                discordBot..StartLobby()
            elif data['eventid'] == EventId.StartTask:
                discordBot..StartTask()

# main関数
def main():
    WebServer()
    DiscordBot()

if __name__ == "__main__":
    main()