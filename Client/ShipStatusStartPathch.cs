using HarmonyLib;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace MuteBotClient {
    [HarmonyPatch(typeof(ShipStatus), nameof(ShipStatus.Start))]
    public static class ShipStatusStartPatch{
        public static void Prefix(){
            MuteBot.LogInfo("ShipStatusStartPatch");
            MuteBot.GetInstance().isGameEnded = false;
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Task));
            return;
        }

    }
}