import shutil
import time
from pathlib import Path
from threading import Lock

import discord

from .base import BaseAction, EventType
from ..discordoptions import DiscordRoles, DiscordChannels


class Sneaky(BaseAction):
    """
        Grants the sneaky challenge role if a message was edited
    """

    def event_type(self) -> EventType:
        return EventType.MessageEdit

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return True

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        channel = await self.client.fetch_channel(self.payload.channel_id)
        message = await channel.fetch_message(self.payload.message_id)

        user = message.author

        async for member in self.client.guilds[0].fetch_members():
            if member.id != user.id:
                continue

            for role in roles:
                if role.name == DiscordRoles.Sneaky:
                    await member.add_roles(role)
                    await self.announce_role(member.id, role.id)


class EavesDropper(BaseAction):
    """
        Trigger the bot playing a Morse message in its own channel.
        This challenge is followed by Beautiful below.
    """

    lock: Lock

    def __init__(self):
        self.lock = Lock()
        self.ffmpeg = shutil.which('ffmpeg')

    @staticmethod
    def media_path(f: str):
        return Path(__file__).resolve(). \
            parent.parent.parent.joinpath('media').joinpath(f)

    def event_type(self) -> EventType:
        return EventType.VoiceStateUpdate

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return True

    async def execute(self):

        # prevent this thing from running awaaaaaay
        if self.lock.locked():
            return

        self.lock.acquire()

        try:

            voice_channels = self.client.guilds[0].voice_channels

            exists = False
            for voice_channel in voice_channels:
                if voice_channel.name == DiscordChannels.BotsOnly:
                    exists = True

            if exists:
                return

            counter = 0

            for voice_channel in voice_channels:
                if len(voice_channel.members) > 0:
                    counter += 1

            if counter > 5:
                for voice_channel in voice_channels:
                    if voice_channel.name == DiscordChannels.BotsOnly:
                        exists = True

                if exists:
                    return

                voice_channel = await self.client.guilds[0].create_voice_channel(DiscordChannels.BotsOnly)
                vc = await voice_channel.connect()
                vc.play(discord.FFmpegPCMAudio(executable=self.ffmpeg,
                                               source=self.media_path('robot_talk.mp3')))
                while vc.is_playing():
                    time.sleep(.1)

                vc.play(discord.FFmpegPCMAudio(executable=self.ffmpeg,
                                               source=self.media_path('robot_countdown.mp3')))
                while vc.is_playing():
                    time.sleep(.1)

                vc.play(discord.FFmpegPCMAudio(executable=self.ffmpeg,
                                               source=self.media_path('morse.mp3')))
                while vc.is_playing():
                    time.sleep(.1)

                await vc.disconnect()
                await voice_channel.delete()
        finally:
            self.lock.release()


class Beautiful(BaseAction):
    """
        Listen to the morse code played in the Bots only challenge
        and spread some love.
    """

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return 'beautiful' in self.message.content.lower() and self.message.guild is None

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue
            for role in roles:
                if role.name == DiscordRoles.Eavesdropper:
                    await member.add_roles(role)
                    await self.announce_role(member.id, role.id)


class MexicanWave(BaseAction):
    """
        Mexican Wave is a challenge where n people type the same message
        and get the role.
    """

    lock: Lock

    def __init__(self):
        self.lock = Lock()

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return self.message.guild

    async def execute(self):

        if self.lock.locked():
            return

        messages = await self.message.channel.history(limit=30).flatten()

        authors = []
        is_first_message = True

        for m in messages:
            if is_first_message:
                authors.append(m.author)
                is_first_message = False
                continue

            if m.content != self.message.content:
                break

            # same author spamming in the last n message is ignored
            new_author = True
            for author in authors:
                if m.author == author:
                    new_author = False
                    break

            if new_author:
                authors.append(m.author)

        if len(authors) < 10:
            return

        await self.message.channel.send('ole! 🌮')

        self.lock.acquire()

        try:
            for role in await self.client.guilds[0].fetch_roles():
                if role.name != DiscordRoles.MexicanWave:
                    continue

                async for member in self.client.guilds[0].fetch_members():

                    # lets not spam folks that already have mexican waves.

                    has_role = False
                    for m_role in member.roles:
                        if m_role.name == DiscordRoles.MexicanWave:
                            has_role = True

                    if has_role:
                        continue

                    for author in authors:
                        if author.id != member.id:
                            continue

                        await member.add_roles(role)
                        await self.announce_role(member.id, role.id)
        finally:
            self.lock.release()
