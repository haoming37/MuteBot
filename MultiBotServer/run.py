import subprocess
import os
from threading import Thread


def launch_kobun(token):

    if getattr(sys, 'frozen', False):
        cmd = "python KOBUN/kobun.exe --token=" + token
    else:
        cmd = "python KOBUN/kobun.py --token=" + token
    subprocess.run(cmd.strip().split(" "))

def launch_oyabun(token):
    if getattr(sys, 'frozen', False):
        cmd = "OYABUN/oyabun.exe --token=" + token
    else:
        cmd = "OYABUN/oyabun.py --token=" + token
    subprocess.run(cmd.strip().split(" "))

def main():
    if getattr(sys, 'frozen', False):
        baseDir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        baseDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(baseDir)

    oyabunToken = ""
    kobunToken = []
    with open("OYABUN_TOKEN", 'r') as f:
        oyabunToken = f.read()
    with open("KOBUN_TOKEN", 'r') as f:
        kobunToken = f.readlines()
    t1 = Thread(target=launch_oyabun, args=(oyabunToken,))
    t1.start()
    kobunThread = []
    for token in kobunToken:
        t = Thread(target=launch_kobun, args=(token,))
        t.start()
        kobunThread.append(t)

if __name__ == "__main__":
    main()


