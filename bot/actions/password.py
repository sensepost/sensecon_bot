from pathlib import Path
import re

from loguru import logger
from pony import orm
from pony.orm import count
import discord

from bot.actions.base import BaseAction, EventType
from ..models import Password


class PasswordUpload(BaseAction):
    """
        Handles password answer uploads
    """

    default_score: int
    challenges: []

    def __init__(self):

        self.challenges = [1, 2, 3]
        self.default_score = 100

        with orm.db_session:
            if count(p for p in Password) > 0:
                return

        logger.info('populating passwords tables with challenge sets')

        # populate the password table
        for challenge in self.challenges:
            logger.debug(f'processing challenge {challenge}')
            with orm.db_session:
                with open(self.password_challenge_clears_path(challenge), 'r') as f:
                    for line in f:
                        Password(challenge=challenge, cleartext=line, value=challenge * self.default_score)

        logger.info('done populating passwords tables with challenge sets')

    @staticmethod
    def password_challenge_clears_path(f: int):
        return Path(__file__).resolve(). \
            parent.parent.parent.joinpath('passwordchal').joinpath(f'{str(f)}_clears.txt')

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


class PasswordDownload(BaseAction):
    """
        Let someone know how many points they have so far.
    """

    # todo: there is a much better way to do this. code repeated in PasswordUpload as well. sorry leon!

    challenges: []

    def __init__(self):

        self.challenges = [1, 2, 3]

    @staticmethod
    def password_challenge_hashes_path(f: int):
        return Path(__file__).resolve(). \
            parent.parent.parent.joinpath('passwordchal').joinpath(f'{str(f)}_hashes.txt')

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        return self.message.content.startswith('!download')

    async def execute(self):
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

        challenge_numbers = re.findall(r'\b\d+\b', self.message.content)

        if len(challenge_numbers) <= 0:
            await self.message.author.send(f'Download command format is `!download <value>`. eg: `!download 1`')
            return

        challenge_number = challenge_numbers[0]

        if int(challenge_number) not in self.challenges:
            await self.message.author.send(f'We only have the following challenges available: {self.challenges}.')
            return

        await self.message.author.send(content='Happy cracking!',
                                       file=discord.File(self.password_challenge_hashes_path(int(challenge_number))))
