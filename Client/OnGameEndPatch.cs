using System.Threading.Tasks;
using HarmonyLib;
using Hazel;
using UnhollowerBaseLib;
using UnityEngine;
// using GameOverReason = AMGMAKBHCMN;


namespace MuteBotClient{
    [HarmonyPatch(typeof(AmongUsClient), nameof(AmongUsClient.OnGameEnd))]
    public class OnGameEndPatch {
        public static void Prefix(AmongUsClient __instance, ref GameOverReason gameOverReason, bool showAd) {
            return;
        }
        public static void Postfix(AmongUsClient __instance, ref GameOverReason gameOverReason, bool showAd) {
            MuteBot.LogInfo("OnGameEndPatch");
            MuteBot.GetInstance().isGameEnded = true;
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Lobby));
            return;
        }
    }
}