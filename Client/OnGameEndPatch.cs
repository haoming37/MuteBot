using System.Threading.Tasks;
using HarmonyLib;
using Hazel;
using UnhollowerBaseLib;
using UnityEngine;
// using GameOverReason = AMGMAKBHCMN;


namespace MuteBotClient{
    //[HarmonyPatch(typeof(AmongUsClient), nameof(AmongUsClient.DDIEDPFFHOG))]
    [HarmonyPatch(typeof(AmongUsClient), nameof(AmongUsClient.OnGameEnd))]
    public class OnGameEndPatch {
        public static void Prefix(AmongUsClient __instance, ref GameOverReason NEPMFBMGGLF, bool FBEKDLNKNLL) {
            return;
        }
        public static void Postfix(AmongUsClient __instance, ref GameOverReason NEPMFBMGGLF, bool FBEKDLNKNLL) {
            MuteBot.LogInfo("OnGameEndPatch");
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Lobby));
            return;
        }
    }
}