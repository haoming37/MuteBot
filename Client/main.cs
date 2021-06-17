using BepInEx;
using BepInEx.Configuration;
using BepInEx.IL2CPP;
using HarmonyLib;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Hazel;
using Logger = BepInEx.Logging.Logger;


namespace MuteBotClient
{
    [BepInPlugin(Id, "MuteBot", "1.0.1")]
    [BepInProcess("Among Us.exe")]
    [BepInDependency("me.eisbison.theotherroles")]
    public class ReplayPlugin : BasePlugin
    {
        public const string Id = "jp.haoming.mutebot";

        public Harmony Harmony { get; } = new Harmony(Id);

        public override void Load()
        {
            // リプレイ保存機能スタート
            Log.LogInfo("Start Haoming.MuteBot");
            MuteBot.GetInstance().logger = Log;

            Harmony.PatchAll();
        }
    }

    // 切断時にBANされるのを無効化する（デバッグ時によく実施するので）
    [HarmonyPatch(typeof(StatsManager), nameof(StatsManager.AmBanned), MethodType.Getter)]
    public static class AmBannedPatch
    {
        public static void Postfix(out bool __result)
        {
            __result = false;
        }
    }
}