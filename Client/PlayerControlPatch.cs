using System;
using System.Text;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Net.Http;
using Newtonsoft.Json;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.IL2CPP;
using HarmonyLib;
using UnityEngine;
using Hazel;

// using SystemTypes = BCPJLGGNHBC;
// using Palette = BLMBFIODBKL;
// using Constants = LNCOKMACBKP;
// using PhysicsHelpers = FJFJIDCFLDJ;
// using DeathReason = EGHDCAKGMKI;
// using GameOptionsData = CEIOGGEDKAN;
// using Effects = AEOEPNHOJDP;

namespace MuteBotClient {
    [HarmonyPatch(typeof(PlayerControl), nameof(PlayerControl.FixedUpdate))]
    public static class PlayerControlFixedUpdatePatch{
        public static void Prefix(PlayerControl __instance) {
            // if (AmongUsClient.Instance.GameState != InnerNet.InnerNetClient.GameStates.Started) return;
            // プレイヤー一覧取得
            List<Player> players = new List<Player>();
            foreach(PlayerControl player in PlayerControl.AllPlayerControls)
            {
                Player p = new Player();
                if(MuteBot.GetInstance().exiledPlayers.Contains(player.name))
                {
                    p.isDead = true;
                }
                else if(MuteBot.GetInstance().killedPlayers.Contains(player.name))
                {
                    p.isDead = true;
                }
                else
                {
                    p.isDead = player.Data.IsDead;
                }
                p.colorId = player.Data.ColorId;
                p.name = player.name;
                players.Add(p);
            }
            if(AmongUsClient.Instance.GameState == InnerNet.InnerNetClient.GameStates.Joined){
                bool flag = false;
                foreach(var player in players)
                {
                    bool isContain = false;
                    foreach(var pplayer in MuteBot.GetInstance().players)
                    {
                        if(pplayer.name == player.name && pplayer.colorId == player.colorId)
                        {
                            isContain = true;
                            break;
                        }
                    }
                    if(!isContain)
                    {
                        flag = true;
                        break;
                    }
                }
                if(flag){
                    MuteBot.GetInstance().players = players;
                    Task t =Task.Run(() => MuteBot.UpdateStatus(GameStatus.Lobby));
                }
            }
        }
        public static void Postfix(PlayerControl __instance) {
            return;
        }
    }

    [HarmonyPatch(typeof(PlayerControl), nameof(PlayerControl.Exiled))]
    public static class PlayerControlExiledPatch
    {
        public static void Postfix(PlayerControl __instance) {
            string name = __instance.name;
            List<Player> players = new List<Player>();
            // 追放されたプレイヤーを死んだ扱いにする
            foreach(Player player in MuteBot.GetInstance().players)
            {
                if(player.name == name)
                {
                    player.isDead = true;
                    MuteBot.GetInstance().exiledPlayers.Add(player.name);
                }
                players.Add(player);
            }
            Task t =Task.Run(() => MuteBot.UpdateStatusExiled(players));
        }
    }
    [HarmonyPatch(typeof(PlayerControl), nameof(PlayerControl.MurderPlayer))]
    public static class MurderPlayerPatch
    {
        public static void Prefix(PlayerControl __instance, PlayerControl DGDGDKCCKHJ)
        {
            // 殺されたプレイヤーを死んだ扱いにする
            foreach(Player player in MuteBot.GetInstance().players)
            {
                if(player.name == DGDGDKCCKHJ.name)
                {
                    MuteBot.GetInstance().killedPlayers.Add(player.name);
                    player.isDead = true;
                }
            }
        }

    }
}