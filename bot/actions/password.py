from pathlib import Path

from loguru import logger
from pony import orm
from pony.orm import count

from bot.actions.base import BaseAction, EventType
from ..models import Password


class PasswordUpload(BaseAction):
    """
        Handles password answer uploads
    """

    default_score: int

    def __init__(self):

        self.default_score = 100

        with orm.db_session:
            if count(p for p in Password) > 0:
                return

        logger.info('populating passwords tables with challenge sets')

        # populate the password table
        for challenge in [1, 2, 3]:
            logger.debug(f'processing challenge {challenge}')
            with orm.db_session:
                with open(self.password_challenge_path(challenge), 'r') as f:
                    for line in f:
                        Password(challenge=challenge, cleartext=line, value=challenge * self.default_score)

        logger.info('done populating passwords tables with challenge sets')

    @staticmethod
    def password_challenge_path(f: int):
        return Path(__file__).resolve(). \
            parent.parent.parent.joinpath('passwordchal').joinpath(f'{str(f)}.txt')

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


class PasswordScore(BaseAction):
    """
        Let someone know how many points they have so far.
    """

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return self.message.content.startswith('!score')

    async def execute(self):
        pass
