using HarmonyLib;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace MuteBotClient {
    [HarmonyPatch(typeof(ShipStatus), nameof(ShipStatus.Start))]
    public static class ShipStatusStartPatch{
        public static void Prefix(){
            MuteBot.LogInfo("ShipStatusStartPatch");
            Task.Run(() =>MuteBot.UpdateOptionsString());

            MuteBot.GetInstance().isGameEnded = false;
            MuteBot.clearExiledPlayers();
            MuteBot.clearKilledPlayers();
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Task));
            return;
        }

    }
}