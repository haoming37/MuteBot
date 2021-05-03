
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
    [HarmonyPatch(typeof(PlayerPhysics), nameof(PlayerPhysics.CoSpawnPlayer))]
    public static class PlayerPhysicsCoSpawnPlayerPatch{
        // ゲーム中
        // InnerNet.InnerNetClient.GameStates.Started
        // ロビー
        // InnerNet.InnerNetClient.GameStates.Joined
        public static void Prefix(LobbyBehaviour JGECHBIEHKM){
            if (AmongUsClient.Instance.GameState != InnerNet.InnerNetClient.GameStates.Started) return;
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Lobby));
            MuteBot.LogInfo("PlayerPhysicsCoSpawnPlayerPatch");
        }
    }
}