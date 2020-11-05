from abc import ABC, abstractmethod
from enum import Enum

import discord
from loguru import logger

from ..discordoptions import DiscordRoles, DiscordChannels


class EventType(Enum):
    """
        Discord events we can handle
    """

    Message = 1
    RawReactionAdd = 2
    RawReactionRemove = 3
    MessageEdit = 4
    MemberJoin = 5
    VoiceStateUpdate = 6
    MemberUpdate = 7


class BaseAction(ABC):
    """
        A BaseAction is a class that implements an action we
        can execute.
    """

    payload: discord.RawReactionActionEvent
    client: discord.client.Client
    message: discord.message.Message
    before: discord.VoiceState
    after: discord.VoiceState

    def set_context(self, client=None, message=None, payload=None, before=None, after=None):
        """
            Sets the context used for the execute method (typically)

            :param client:
            :param message:
            :param payload:
            :param before:
            :param after:
            :return:
        """

        self.client = client
        self.message = message
        self.payload = payload
        self.before = before
        self.after = after

    async def is_verified(self, member: discord.guild.Member, alert=False) -> bool:
        """
            Checks if a member has the verified role.

            :param member:
            :param alert:
            :return:
        """

        for user_roles in member.roles:
            if user_roles.name == DiscordRoles.Verified:
                return True

        if alert:
            await member.send(
                "Please verify your account first. \n"
                "To verify your account, send me a message with `!verify ` and your "
                "@orangecyberdefense.com email address so that I can send you an OTP.")

            if self.message.guild:
                await self.message.channel.send("<@{}> I have sent you a DM".format(self.message.author.id))

        return False

    @staticmethod
    async def member_has_role(member: discord.client.Member, role: DiscordRoles):
        """
            Check's if a member has a Role

            :param member:
            :param role:
            :return:
        """

        for m_role in member.roles:
            if m_role.name == role:
                return True

        return False

    async def send_channel_message(self, message: str, channel: DiscordChannels):
        """
            Send a message to a channel.

            :param message:
            :param channel:
            :return:
        """

        for ch in await self.client.guilds[0].fetch_channels():
            if ch.name != channel or not isinstance(ch, discord.TextChannel):
                continue

            await ch.send(f'{message}')

    async def grant_member_role(self, member: discord.client.Member, role: DiscordRoles, announce=True):
        """
            Grants a member a role if they don't already have it.

            :param member:
            :param role:
            :param announce:
            :return:
        """

        has_role = False
        for m_role in member.roles:
            if m_role.name == role:
                has_role = True

        if has_role:
            logger.info(f'{member.nick if member.nick else member.display_name} already has the {role} role')
            return

        discord_roles = await self.client.guilds[0].fetch_roles()

        for discord_role in discord_roles:
            if discord_role.name != role:
                continue

            logger.info(f'granting role {role} to {member.nick if member.nick else member.display_name}')
            await member.add_roles(discord_role)

            if announce:
                await self.announce_role(member.id, discord_role.id)

    async def announce_role(self, member, role):
        """
            Send a message to the roles channel

            :param member:
            :param role:
            :return:
        """

        await self.send_channel_message(f'<@{member}> just got the <@&{role}> role!', DiscordChannels.Roles)

    @abstractmethod
    def event_type(self) -> EventType:
        pass

    @abstractmethod
    def should_stop(self) -> bool:
        pass

    @abstractmethod
    def match(self) -> bool:
        pass

    @abstractmethod
    async def execute(self):
        pass
