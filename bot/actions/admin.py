from loguru import logger

from ..actions.base import BaseAction, EventType
from ..discordoptions import DiscordRoles, DiscordChannels


class Admin(BaseAction):

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        pass

    async def execute(self):
        pass

    async def get_channel(self, channel_name: str, category_name: str):
        category = None

        categories = self.client.guilds[0].categories

        for cat in categories:
            if cat.name.lower() != category_name.lower():
                continue

            category = cat

        if category is None:
            return None

        channels = await self.client.guilds[0].fetch_channels()
        for channel in channels:
            if channel.category_id != category.id or channel.name != channel_name:
                continue

            return channel


class SendMessage(Admin):
    """
        Let's an admin send a message.
    """

    def match(self) -> bool:
        return self.message.content.startswith('!send')

    async def execute(self):

        # ignore non DMs
        if self.message.guild is not None:
            return

        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            # ignore non admins
            if not await self.member_has_role(member, DiscordRoles.Admin):
                await member.send('you are not an admin it seems')
                return

            # parse message
            # expected format should be !send\n<category.channel>\n<message>
            message = self.message.content
            parts = message.split('\n')

            channel_parts = parts[1].split('.')
            channel_name = channel_parts[1]
            category_name = channel_parts[0]
            message = '\n'.join(parts[2:])

            logger.info(f'parsed message category.channel: {parts[1]}')
            logger.info(f'parsed message message: {parts[2]}')

            channel = await self.get_channel(channel_name, category_name)

            if channel is None:
                await member.send(f'could not find channel: {channel_name} in {category_name}')
                return

            await channel.send(f'{message}')
            logger.info(f'member sent message as sysmon: {member.name} sent a message in {category_name}.{channel.name}')


class ClearChatChannel(Admin):
    """
        Let's an admin delete all messages in a channel.
    """

    def match(self) -> bool:
        return self.message.content.startswith('!clear')

    async def execute(self):

        # ignore non DMs
        if self.message.guild is not None:
            return

        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            # ignore non admins
            if not await self.member_has_role(member, DiscordRoles.Admin):
                await member.send('you are not an admin it seems')
                return

            channel_parts = self.message.content.split(' ')[1].split('.')

            channel_name = channel_parts[1]
            category_name = channel_parts[0]

            channel = await self.get_channel(channel_name, category_name)

            if channel is None:
                await member.send(f'could not find channel: {channel_name} in {category_name}')
                return

            logger.info(f'purging channel: {channel.name}')
            await channel.purge()
            logger.info(f'purged channel: {channel.name} in {category_name}')
