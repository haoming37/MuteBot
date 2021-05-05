using HarmonyLib;
using System.Threading.Tasks;

namespace MuteBotClient {
    [HarmonyPatch(typeof(MeetingHud), nameof(MeetingHud.Awake))]
    public class MeetingHudAwakePatch{
        public static void Postfix(){
            MuteBot.LogInfo("MeetingHudAwakePatch");
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Discussion));
        }
    }
    [HarmonyPatch(typeof(MeetingHud), nameof(MeetingHud.Close))]
    public class MeetingHudClosePatch{
        public static void Postfix(){
            MuteBot.LogInfo("MeetingHudClosePatch");
            Task.Run(() => MuteBot.UpdateStatus(GameStatus.Task));
        }
    }
}