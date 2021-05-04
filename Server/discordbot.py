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
    nameConverter = {}
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
            print(content)
            if command == "new" or command == "n":
                await discordbot.new(message)
            elif command == "end" or command == "e":
                await discordbot.end(message)
            elif command == "unmute" or command == "u":
                await discordbot.unmute(message)
            elif command == "list" or command == "l":
                await discordbot.linkList(message)
            else:
                await discordbot.help(message)
        elif re.match('^/msm link .* .*$', content):
            print(content)
            await discordbot.link(message)

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
        self.msg = await message.channel.send("MuteBot開始\nクライアント待ち")
        self.vc = targetvc
        self.isRunning = True

    async def end(self, message):
        # ミュートを解除する
        await self.unmute(message)
        # サーバー起動のメッセージを削除する
        if self.isRunning:
            await self.msg.delete()
            self.vc = None
            self.msg = None
            self.isRunning = False
            with open(baseDir +"/nameConverter.json", "w") as f:
                json.dump(self.nameConverter,f)
        else:
            message.channel.send("MuteBotが起動していません")

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

    async def link(self, message):
        args = message.content.strip().split(" ")
        self.nameConverter[args[2]] = args[3]
        text = args[2] + "(Among Us)を" + args[3] + "(Discord)にリンクしました"
        await message.channel.send(text)
    
    async def linkList(self, message):
        text = "[リンクリスト]\n"
        for item in self.nameConverter:
            text = item + "(Among Us)と" + self.nameConverter[item] + "(Discord)がリンクされています\n" 
        await message.channel.send(text)


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

    async def help(self, message):
        text = """
        ```
        使い方
        /msm new
        /msm end
        /msm unmute
        /msm link <AmongUsプレイヤー名> <Discord表示名>
        ※ロビーで色を変える、入り直す等をすると反映されます
        ```
        """
        await message.channel.send(text)

    # ゲーム開始時、ミーティング終了時に実行
    async def startTask(self, players):
        if self.msg == None:
            return
        print("startTasks")
        for player in players:
            flag = True
            target = None
            convertedName = ""
            if player['name'] in self.nameConverter:
                userid = self.nameConverter[player['name']].replace("<@!", "").replace(">", "")
                if userid.isdecimal:
                    convertedName = self.msg.guild.get_member(int(userid)).display_name

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
            convertedName = ""
            if player['name'] in self.nameConverter:
                userid = self.nameConverter[player['name']].replace("<@!", "").replace(">", "")
                if userid.isdecimal:
                    convertedName = self.msg.guild.get_member(int(userid)).display_name
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
        text = "```"
        text += "MuteBot動作中```"
        for player in players:
            text += player['name'] + " <=> "

            if player['name'] in self.nameConverter:
                userid = self.nameConverter[player['name']].replace("<@!", "").replace(">", "")
                convertedName = self.msg.guild.get_member(int(userid)).display_name
            else:
                convertedName = ""
            flag = True
            for member in self.vc.members:
                if convertedName == member.display_name or player['name'] == member.display_name:
                    text += "<@" + str(member.id) + ">"
                    flag = False
            if flag:
                text += "Not Linked"
            # text += " colorId=" + str(player['colorId'])
            # text += " " + str(player['isDead'])
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
        # サーバーが起動していることを確認する用
        return 'Hello, World!'

# main関数
def startDiscordBot():
    DiscordBot().client.run(TOKEN)

def main():
    thread1 = Thread(target=startDiscordBot)
    thread1.start()
    app.run('0.0.0.0', port=8080)
    thread1.join()

if __name__ == "__main__":
    main()