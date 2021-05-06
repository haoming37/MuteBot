import discord
import json
import os, sys
from singleton_decorator import singleton
from threading import Thread
import asyncio
import socket
import time
import re, shlex

Intents = discord.Intents.default()
Intents.members = True

if getattr(sys, 'frozen', False):
    baseDir = os.path.dirname(os.path.abspath(sys.executable))
else:
    baseDir = os.path.dirname(os.path.abspath(__file__))
TOKENPATH = baseDir + "/KOBUN_TOKEN"
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
        if re.match('^/msm [a-z].*$', content):
            command = shlex.split(content)[1]
            print(content)
            if command == "new" or command == "n":
                await discordbot.new(message)

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
        self.msg = await message.channel.send("Misimoの子分準備完了")
        self.vc = targetvc
        self.isRunning = True

    async def setVoiceStatus(self,voicestatus):
        if self.isRunning and self.vc:
            print("setVoiceStatus")
            print(voicestatus)
            try:
                for member in self.vc.members:
                    name = member.display_name
                    if name in voicestatus:
                        while voicestatus[name]['mute'] != member.voice.mute:
                            await member.edit(mute=voicestatus[name]['mute'])
                        while voicestatus[name]['deafen'] != member.voice.deaf:
                            await member.edit(deafen=voicestatus[name]['deafen'])
            except Exception as e:
                print(e)

# main関数
def startDiscordBot():
    DiscordBot().client.run(TOKEN)

def socketClient():
    HOST = "127.0.0.1"
    PORT = 65340
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:
                    jsonBytes = bytes()
                    s.sendall(b'REQ\0')
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        jsonBytes += data
                        if data[-1] == 0x00:
                            jsonBytes = jsonBytes[:-1]
                            decoded = jsonBytes.decode("utf-8")
                            if(decoded != 'NONE'):
                                print(jsonBytes)
                                print(decoded)
                                try:
                                    js = json.loads(decoded)
                                    print(js)
                                    db = DiscordBot()
                                    client = db.client
                                    function = asyncio.run_coroutine_threadsafe(db.setVoiceStatus(js), client.loop)
                                    function.result()
                                except Exception as e:
                                    print(e)
                            jsonBytes = bytes()
                            break
                    if not data:
                        break
                    time.sleep(0.1)
        except Exception as e:
            print(e)
    time.sleep(10)


def main():
    thread1 = Thread(target=startDiscordBot)
    thread1.start()
    thread2 = Thread(target=socketClient)
    thread2.start()
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    main()

# main関数
def startDiscordBot():
    DiscordBot().client.run(TOKEN)
