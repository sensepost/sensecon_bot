import re
from pathlib import Path

import discord
from loguru import logger
from pony import orm
from pony.orm import count
from pony.orm import select

from bot.actions.base import BaseAction, EventType
from ..discordoptions import DiscordRoles, DiscordChannels
from ..models import Password, User, PasswordScoreLog


class PasswordChallengeBase(BaseAction):
    """
        A base password challenge class
    """

    challenges: []

    def __init__(self):
        self.challenges = [1, 2, 3, 4]

    @staticmethod
    def get_points(user):
        with orm.db_session:
            counter = 0
            points_logged = select(l for l in PasswordScoreLog if l.user == user)

            for point in points_logged:
                counter += point.points

            return counter

    @staticmethod
    def password_challenge_path(f: int, t: str):
        """
            Reads a challenge file from the password challenge path.

            :param f:str the file to read
            :param t:str the challenge type to read
            :return:
        """

        return Path(__file__).resolve(). \
            parent.parent.parent.joinpath('passwordchal').joinpath(f'{str(f)}_{t}.txt')

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return False

    def match(self) -> bool:
        pass

    async def execute(self):
        pass


class PasswordUpload(PasswordChallengeBase):
    """
        Handles password answer uploads
    """

    default_score: int

    def __init__(self):
        super().__init__()
        self.default_score = 100
        self.seed_db()

    def seed_db(self):
        with orm.db_session:
            if count(p for p in Password) > 0:
                return

        logger.info('populating passwords tables with challenge sets')

        # populate the password table
        for challenge in self.challenges:
            logger.debug(f'processing challenge {challenge}')
            with orm.db_session:
                with open(self.password_challenge_path(challenge, 'clears'), 'r') as f:
                    for line in f:
                        Password(challenge=challenge, cleartext=line, value=challenge * self.default_score)

        logger.info('done populating passwords tables with challenge sets')

    def match(self) -> bool:
        return self.message.content.startswith('!submit')

    async def execute(self):
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

            if len(self.message.attachments) <= 0:
                await self.message.author.send(f'I think you forgot to attach your submission_file.')
                return

            if len(self.message.attachments) > 1:
                await self.message.author.send(f'For now we only accept one upload at a time.')
                return

            challenge_numbers = re.findall(r'\b\d+\b', self.message.content)

            if len(challenge_numbers) <= 0:
                await self.message.author.send(f'Submit command format is `!download <value>` together with an '
                                               f'attachment. eg: `!submit 1`')
                return

            challenge_number = challenge_numbers[0]

            if int(challenge_number) not in self.challenges:
                await self.message.author.send(f'We only have the following challenges available: {self.challenges}.')
                return

            attachment = self.message.attachments[0]
            if attachment.size > 200000:
                await self.message.author.send(
                    f'Woah buddy, how about you go crack it yourself. Maybe we should take away 5000 points from your '
                    f'score.')
                await self.grant_member_role(member, DiscordRoles.Lazy, announce=True)
                return

            file = await attachment.read(use_cached=False)
            submission_file = file.decode("utf-8")
            submission = submission_file.splitlines()

            new_submission = self.remove_duplicates(member.id, int(challenge_number), submission)
            correct, total = self.check_and_score(member.id, challenge_number, new_submission)

            with orm.db_session:
                user = select(s for s in User if s.userid == member.id).first()

                await self.message.author.send(
                    f'Your submission has been processed. You have cracked {correct} of the {total} hashes.'
                    f' You now have a total of {self.get_points(user)} points.')

                if correct == 0:
                    return

                await self.send_channel_message(f'<@{self.message.author.id}> just submitted {correct} passwords!',
                                                DiscordChannels.Sconwar)

    @staticmethod
    def remove_duplicates(user, challenge, submission):

        submitted_correct_passwords = []

        with orm.db_session:
            submitted_passwords = select(s for s in User if s.userid == user).first().passwords_cracked

            for password in submitted_passwords:
                if password.challenge != challenge:
                    continue

                submitted_correct_passwords.append(password.cleartext)

            # remove any of the passwords we have already cracked
            return set(set(submission) - set(submitted_correct_passwords))

    @staticmethod
    def check_and_score(user, challenge, new_passwords):

        with orm.db_session:
            user = select(s for s in User if s.userid == user).first()

            valid_passwords = select(p for p in Password if p.challenge == challenge)

            correct = 0

            for password in valid_passwords:
                if password.cleartext not in new_passwords:
                    continue

                PasswordScoreLog(user=user, points=password.value, cleartext=password.cleartext)

                if password.value != 0:
                    password.value -= 1

                user.passwords_cracked.add(password)

                correct += 1

            return correct, len(valid_passwords)


class PasswordScore(PasswordChallengeBase):
    """
        Let someone know how many points they have so far.
    """

    def __init__(self):
        super().__init__()

    def match(self) -> bool:
        return self.message.content.startswith('!score')

    async def execute(self):
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

            with orm.db_session:
                user = select(s for s in User if s.userid == member.id).first()

                await self.message.author.send(f'You have {self.get_points(user)} points.')


class PasswordDownload(PasswordChallengeBase):
    """
        Let someone know how many points they have so far.
    """

    def __init__(self):
        super().__init__()

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
                                       file=discord.File(self.password_challenge_path(int(challenge_number), 'hashes')))
