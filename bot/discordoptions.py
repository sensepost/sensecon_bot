from dataclasses import dataclass, fields

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

    def key_by_name(self, n):
        for field in fields(self):
            if field.value == n:
                return field.name
