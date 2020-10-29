from bot.actions.base import BaseAction, EventType


class PasswordUpload(BaseAction):
    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return self.message.content.startswith('!submit')

    async def execute(self):
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return
