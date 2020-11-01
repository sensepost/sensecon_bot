from loguru import logger

from .base import BaseAction, EventType
from ..discordoptions import DiscordChannels, EmojiRoleMap, DiscordRoles


class CountryFlag(BaseAction):

    def event_type(self) -> EventType:
        pass

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return True

    async def execute(self):
        pass


class CountryFlagAdd(CountryFlag):
    """
        CountryFlag adds a country related role based on an emoji reaction
    """

    def event_type(self) -> EventType:
        return EventType.RawReactionAdd

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        channel = await self.client.fetch_channel(self.payload.channel_id)

        if channel.name != DiscordChannels.Lobby:
            return

        message = await channel.fetch_message(self.payload.message_id)

        if "Welcome to SenseCon 2020" not in message.content:
            return

        computer_flag = False

        # want to clear that computer flag asap
        if 'computer' == EmojiRoleMap[self.payload.emoji.name]:
            await message.clear_reaction(self.payload.emoji.name)
            computer_flag = True

        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.payload.user_id:
                continue

            if self.payload.emoji.name not in EmojiRoleMap:
                logger.debug(f'{self.payload.emoji.name} is not in our role map')
                continue

            for role in roles:
                if role.name != EmojiRoleMap[self.payload.emoji.name]:
                    continue

                # don't use self.grant_.. as the role mapping is odd here.
                logger.debug(f'granting a user the {self.payload.emoji.name} role')
                await member.add_roles(role)

            if computer_flag:
                await self.grant_member_role(member, DiscordRoles.Fuzzer, announce=True)


class CountryFlagRemove(CountryFlag):
    """
        Removes a role when the country flag reaction is removed
    """

    def event_type(self) -> EventType:
        return EventType.RawReactionRemove

    async def execute(self):
        roles = await self.client.guilds[0].fetch_roles()
        channel = await self.client.fetch_channel(self.payload.channel_id)

        if channel.name != DiscordChannels.Lobby:
            return

        message = await channel.fetch_message(self.payload.message_id)

        if "Welcome to SenseCon 2020" not in message.content:
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
