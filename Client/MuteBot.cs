using System;
using System.Text;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Net.Http;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.IL2CPP;
using UnhollowerBaseLib;
using HarmonyLib;
using UnityEngine;
using Hazel;
using Newtonsoft.Json;

namespace MuteBotClient{
    public sealed class MuteBot{
        public bool isServerActive = true;
        public BepInEx.Logging.ManualLogSource logger = null;
        private static MuteBot _instance = new MuteBot();
        public static MuteBot GetInstance() { return _instance;}
        public string url = "http://localhost:8080/mutebot";
        private bool isRunning = false;
        private Timer timer;
        public List<Player> players = new List<Player>();
        public Game game = new Game();

        public static void LogInfo(string msg){
            if(_instance.logger != null){
                _instance.logger.LogInfo(msg);
            }
        }

        // 会議終了後のみに呼び出す専用関数
        public static void UpdateStatusDelay()
        {
            TimerCallback timerDelegate = new TimerCallback(OntimerEvent);
            _instance.timer = new Timer(timerDelegate, null , 5000, 5000);
        }
        private static void OntimerEvent(object o)
        {
            Task t =Task.Run(() => UpdateStatus(GameStatus.Task));
            _instance.timer.Dispose();
        }
        
        public static async Task UpdateStatus(GameStatus status){
            if(!_instance.isServerActive) return;
            LogInfo("UpdateStatus");
            Game game = new Game();
            game.gameStatus = status;
            game.players = _instance.players;
            string json =JsonConvert.SerializeObject(game);
            using(var client = new HttpClient())
            {
                var content = new StringContent(json, Encoding.UTF8);
                var response = await client.PostAsync(_instance.url, content);
                if (!response.IsSuccessStatusCode)
                {
                    _instance.isServerActive = false;
                }
            }
            return;
        }
    }
}