from loguru import logger

from ..actions.base import BaseAction, EventType
from ..discordoptions import DiscordRoles, DiscordChannels


class SendMessage(BaseAction):
    """
        Let's an admin send a message.
    """

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

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

            # todo: split category . channel still
            channel = parts[1]
            message = parts[2]

            logger.info(f'parsed message category.channel: {parts[1]}')
            logger.info(f'parsed message message: {parts[2]}')

            await self.send_channel_message(parts[2], DiscordChannels.General)
