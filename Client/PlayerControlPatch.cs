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
            if (AmongUsClient.Instance.GameState != InnerNet.InnerNetClient.GameStates.Started) return;
            // プレイヤー一覧取得
            List<Player> players = new List<Player>();
            foreach(PlayerControl player in PlayerControl.AllPlayerControls)
            {
                Player p = new Player();
                p.isDead = player.Data.IsDead;
                p.colorId = player.Data.ColorId;
                p.name = player.name;
                players.Add(p);
            }
            MuteBot.GetInstance().players = players;
        }
        public static void Postfix(PlayerControl __instance) {
            return;
        }
    }
}