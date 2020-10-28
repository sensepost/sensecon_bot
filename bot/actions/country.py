from loguru import logger

from .base import BaseAction, EventType
from ..discordoptions import DiscordChannels, EmojiRoleMap


class CountryFlagAdd(BaseAction):
    """
        CountryFlag adds a country related role based on an emoji reaction
    """

    def event_type(self) -> EventType:
        return EventType.RawReactionAdd

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return True

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        channel = await self.client.fetch_channel(self.payload.channel_id)

        if channel.name != DiscordChannels.Lobby:
            return

        message = await channel.fetch_message(self.payload.message_id)

        if "Welcome all to SenseCon 2020." not in message.content:
            return

        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.payload.user_id:
                continue

            if self.payload.emoji.name not in EmojiRoleMap:
                logger.debug(f'{self.payload.emoji.name} is not in our role map')
                continue

            for role in roles:
                if role.name != EmojiRoleMap[self.payload.emoji.name]:
                    continue

                logger.debug(f'granting a user the {self.payload.emoji.name} role')
                await member.add_roles(role)
                await self.announce_role(member.id, role.id)


class CountryFlagRemove(BaseAction):
    """
        Removes a role when the country flag reaction is removed
    """

    def event_type(self) -> EventType:
        return EventType.RawReactionRemove

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return True

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        channel = await self.client.fetch_channel(self.payload.channel_id)

        if channel.name != DiscordChannels.Lobby:
            return

        message = await channel.fetch_message(self.payload.message_id)

        if "Welcome all to SenseCon 2020." not in message.content:
            return

        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.payload.user_id:
                continue

            if self.payload.emoji.name not in EmojiRoleMap:
                logger.debug(f'{self.payload.emoji.name} is not in our role map')
                continue

            for role in roles:
                if role.name != EmojiRoleMap[self.payload.emoji.name]:
                    continue

                logger.debug(f'removing the {self.payload.emoji.name} role from a user')
                await member.remove_roles(role)
