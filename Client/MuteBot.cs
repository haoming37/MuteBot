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
using TheOtherRoles;
using System.Text.RegularExpressions;

namespace MuteBotClient{
    public sealed class MuteBot{
        public bool isServerActive = true;
        public bool isGameEnded = false;
        public BepInEx.Logging.ManualLogSource logger = null;
        private static MuteBot _instance = new MuteBot();
        public static MuteBot GetInstance() { return _instance;}
        public string url = "http://18.177.110.86:8080/mutebot";
        public string code = "";
        private Timer timer;
        public List<Player> players = new List<Player>();
        public List<string> exiledPlayers = new List<string>();
        public List<string> killedPlayers = new List<string>();
        public Game game = new Game();
        private string oldText = "";
        private bool isOptionsStringWorking = false;

        public static void LogInfo(string msg){
            if(_instance.logger != null){
                _instance.logger.LogInfo(msg);
            }
        }
        public static void clearExiledPlayers(){
            _instance.exiledPlayers = new List<string>();
        }
        public static void clearKilledPlayers(){
            _instance.killedPlayers = new List<string>();
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

        public static async Task UpdateStatusExiled(List<Player> players){
            LogInfo("UpdateStatusExiled");
            if(!_instance.isGameEnded)
            {
                Game game = new Game();
                game.code = _instance.code;
                game.gameStatus = GameStatus.Task;
                game.players = players;
                string json = JsonConvert.SerializeObject(game);
                using(var client = new HttpClient())
                {
                    var content = new StringContent(json, Encoding.UTF8);
                    var response = await client.PostAsync(_instance.url, content);
                    if (!response.IsSuccessStatusCode)
                    {
                        LogInfo("Post失敗");
                        _instance.isServerActive = false;
                    }
                }
            }
            else
            {
                await UpdateStatus(GameStatus.Lobby);
            }
            return;
        }
        
        public static async Task UpdateStatus(GameStatus status){
            LogInfo("UpdateStatus");
            Game game = new Game();
            game.gameStatus = status;
            game.code = _instance.code;
            if(status == GameStatus.Lobby)
            {
               _instance.exiledPlayers = new List<string>();
               _instance.killedPlayers = new List<string>();
            }

            foreach(Player player in _instance.players)
            {
                if(_instance.exiledPlayers.Contains(player.name) || _instance.killedPlayers.Contains(player.name)){
                    player.isDead = true;
                }
            }
            game.players = _instance.players;
            string json = JsonConvert.SerializeObject(game);
            using(var client = new HttpClient())
            {
                var content = new StringContent(json, Encoding.UTF8);
                var response = await client.PostAsync(_instance.url, content);
                if (!response.IsSuccessStatusCode)
                {
                    LogInfo("Post失敗");
                    _instance.isServerActive = false;
                }
            }
            return;
        }

        public static async Task UpdateOptionsString(){
            //LogInfo("UpdateOptionsString");
            if(_instance.isOptionsStringWorking){
                return;
            }
            _instance.isOptionsStringWorking = true;
            CustomOptions co = new CustomOptions();
            co.optionsString = "";
            StringBuilder sb = new StringBuilder();
            string crew = "";
            string neutral = "";
            foreach(TheOtherRoles.CustomOption option in TheOtherRoles.CustomOption.options){
                if(option.parent == null){
                    if (option == CustomOptionHolder.crewmateRolesCountMin) {
                        var optionName = CustomOptionHolder.cs(new Color(204f / 255f, 204f / 255f, 0, 1f), "Crewmate Roles");
                        var min = CustomOptionHolder.crewmateRolesCountMin.getSelection();
                        var max = CustomOptionHolder.crewmateRolesCountMax.getSelection();
                        if (min > max) min = max;
                        var optionValue = (min == max) ? $"{max}" : $"{min} - {max}";
                        crew = $"{optionName}: {optionValue}";
                    } else if (option == CustomOptionHolder.neutralRolesCountMin) {
                        var optionName = CustomOptionHolder.cs(new Color(204f / 255f, 204f / 255f, 0, 1f), "Neutral Roles");
                        var min = CustomOptionHolder.neutralRolesCountMin.getSelection();
                        var max = CustomOptionHolder.neutralRolesCountMax.getSelection();
                        if (min > max) min = max;
                        var optionValue = (min == max) ? $"{max}" : $"{min} - {max}";
                        neutral = $"{optionName}: {optionValue}";
                    } else if (option == CustomOptionHolder.impostorRolesCountMin) {
                        var optionName = CustomOptionHolder.cs(new Color(204f / 255f, 204f / 255f, 0, 1f), "Impostor Roles");
                        var min = CustomOptionHolder.impostorRolesCountMin.getSelection();
                        var max = CustomOptionHolder.impostorRolesCountMax.getSelection();
                        if (min > max) min = max;
                        var optionValue = (min == max) ? $"{max}" : $"{min} - {max}";
                        sb.AppendLine("");
                        sb.AppendLine($"{optionName}: {optionValue}");
                        sb.AppendLine("```ARM");
                    } else if ((option == CustomOptionHolder.crewmateRolesCountMax) || (option == CustomOptionHolder.neutralRolesCountMax) || (option == CustomOptionHolder.impostorRolesCountMax)) {
                        continue;
                    } else{
                        string percent = option.selections[option.selection].ToString();
                        if(percent != "0%"){
                            string name = Regex.Replace(option.name, " ", "");
                            name = Regex.Replace(name, "<[^>]*>", "");
                            percent = Regex.Replace(percent, "%", "");
                            string text = "";
                            if(name.Length < 15){
                                int diff = 15 - name.Length;
                                if(percent == "100"){
                                    diff -= 1;
                                }
                                text = $"{name}: ";
                                for(int i=0; i<diff; i++){
                                    text += "  ";
                                }
                                text += percent;
                            }
                            else{
                                text = $"{name}: {percent}";
                            }
                            sb.AppendLine(text);
                        }

                        // 役職追加をしたら修正必要
                        if(option.name.Contains("漢") || option.name.Contains("ジャッカル") || option.name.Contains("無能")){
                            sb.AppendLine("```");
                            // sb.AppendLine("");
                            if(option.name.Contains("漢")){
                                sb.AppendLine(neutral);
                                sb.AppendLine("```yaml");
                            }
                            if(option.name.Contains("ジャッカル")){
                                sb.AppendLine(crew);
                                sb.AppendLine("```CSS");
                            }
                        }
                    }
                }
            }

            co.optionsString = Regex.Replace(sb.ToString(), "<[^>]*>", "");
            if(_instance.oldText == co.optionsString){
                _instance.isOptionsStringWorking = false;
                return;
            }
            _instance.oldText = co.optionsString;
            LogInfo(co.optionsString);
            string json = JsonConvert.SerializeObject(co);
            using(var client = new HttpClient())
            {
                var content = new StringContent(json, Encoding.UTF8);
                var response = await client.PostAsync(_instance.url, content);
                if (!response.IsSuccessStatusCode)
                {
                    LogInfo("Post失敗");
                    _instance.isServerActive = false;
                }
            }
            _instance.isOptionsStringWorking = false;
            return;
        }
    }
}