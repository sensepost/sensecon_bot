from dataclasses import dataclass

EmojiRoleMap = {
    '🇳🇴': "norway",
    '🇧🇪': "belgium",
    '🇬🇧': "united kingdom",
    '🇸🇪': "sweden",
    '🇳🇱': "netherlands",
    '🇿🇦': "south africa",
    '🇲🇦': "morocco",
    '🇫🇷': "france",
    '💻': "computer",
}


@dataclass
class DiscordRoles:
    Admin = "admin"
    Verified = "verified"
    Sneaky = "challenge:sneaky"
    Eavesdropper = "challenge:eavesdropper"
    Hacker = "challenge:hacker"
    MexicanWave = "challenge:mexican wave"
    Lazy = "lazy"
    Fuzzer = "challenge:fuzzer"


@dataclass
class DiscordChannels:
    Lobby = "lobby"
    Roles = "roles"
    BotsOnly = "Bots only"
    General = "general"
    Sconwar = "sconwar"
