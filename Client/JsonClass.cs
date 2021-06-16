using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json;
// using BepInEx;
// using BepInEx.Configuration;
// using TheOtherRoles;
// using SystemTypes = BCPJLGGNHBC;
// using SwitchSystem = ABIMJJMBJJM;
// using ISystemType = JBBCJFNFOBB;
// using GameOverReason = AMGMAKBHCMN;

namespace MuteBotClient{
    public enum GameStatus{
        Lobby,
        Task,
        Discussion,
        UNKNOWN
    }
    public class Player{
        public string name{ get; set;}
        public bool isDead{get; set;}
        public int colorId{get; set;}

        public Player(){
            name = "";
            isDead = false;
            colorId = 0;
        }
    } 
    public class Game{
        public GameStatus gameStatus{get; set;}
        public List<Player> players{get; set;}
        public string code{get; set;}
        public Game(){
            players = new List<Player>();
            gameStatus = GameStatus.UNKNOWN;
            code = "";
        }
    }
    public class CustomOptions{
        public string optionsString{get; set;}
        public CustomOptions(){
            optionsString = "";
        }
    }
}