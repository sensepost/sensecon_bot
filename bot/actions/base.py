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

    def set_context(self, client=None, message=None, payload=None):
        """
            Sets the context used for the execute method (typically)

            :param client:
            :param message:
            :param payload:
            :return:
        """

        self.client = client
        self.message = message
        self.payload = payload

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
            logger.debug(f'{member.nick if member.nick else member.display_name} already has the {role} role')
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

        for channel in await self.client.guilds[0].fetch_channels():
            if channel.name != DiscordChannels.Roles or not isinstance(channel, discord.TextChannel):
                continue

            await channel.send(f'<@{member}> just got the <@&{role}> role!')

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
