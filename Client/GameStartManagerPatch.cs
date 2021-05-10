using HarmonyLib;
using UnityEngine;
using System.Collections.Generic;
using Hazel;
using System;
using UnhollowerBaseLib;
using System.Threading.Tasks;

namespace MuteBotClient {
    public class GameStartManagerPatch  {
        [HarmonyPatch(typeof(GameStartManager), nameof(GameStartManager.Update))]
        public class GameStartManagerUpdatePatch {
            public static void Postfix(GameStartManager __instance) {
                string code = InnerNet.GameCode.IntToGameName(AmongUsClient.Instance.GameId);
                if(MuteBot.GetInstance().code != code)
                {
                    MuteBot.GetInstance().code = code;
                    Task.Run(() => MuteBot.UpdateStatus(GameStatus.Lobby));
                }
            }
        }
    }
}