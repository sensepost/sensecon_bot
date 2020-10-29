from pathlib import Path
import re
import io

from loguru import logger
from pony import orm
from pony.orm import count
from pony.orm import select
import discord

from bot.actions.base import BaseAction, EventType
from ..discordoptions import DiscordRoles
from ..models import Password, User, PasswordScoreLog


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

                #todo: think about this one

                #with orm.db_session:
                #    user = select(s for s in User if s.userid == member.id).first()
                #    user.points = -5000

                await self.message.author.send(
                    f'Woah buddy, how about you go crack it yourself. Also, we took away 5000 points from your score.')
                await self.grant_member_role(member, DiscordRoles.Lazy, announce=True)

            else:
                file = await attachment.read(use_cached=False)
                submission_file = file.decode("utf-8")
                submission = submission_file.splitlines()

                new_submission = self.remove_duplicates(member.id, int(challenge_number), submission)
                self.check_and_score(member.id, challenge_number, new_submission)

                with orm.db_session:
                    user = select(s for s in User if s.userid == member.id).first()

                    await self.message.author.send(
                        f'Your submission has been processed, you now have {self.get_points(user)} points.')

    @staticmethod
    def get_points(user):
        with orm.db_session:
            counter = 0
            points_logged = select(l for l in PasswordScoreLog if l.user == user)

            for point in points_logged:
                counter += point.points

            return counter

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

            for password in valid_passwords:
                if password.cleartext not in new_passwords:
                    continue

                PasswordScoreLog(user=user, points=password.value, cleartext=password.cleartext)

                if password.value != 0:
                    password.value -= 1

                user.passwords_cracked.add(password)


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
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

            if "debug" not in self.message.content:
                with orm.db_session:
                    user = select(s for s in User if s.userid == member.id).first()

                    await self.message.author.send(f'You have {self.get_points(user)} points.')
                return

            with orm.db_session:
                user = select(s for s in User if s.userid == member.id).first()

                logs = select(l for l in PasswordScoreLog if l.user == user)

                file = io.StringIO()

                output = []

                for log in logs:
                    output.append(f'You got {log.points} for the submission of {log.cleartext}')

                # todo: fix me

                file.write('\n'.join(x for x in output))

                await self.message.author.send(content=f'You have {self.get_points(user)} points.', file=discord.File(file, filename='logs.txt'))

                file.close()




    # todo: another dupe from above class.

    @staticmethod
    def get_points(user):
        with orm.db_session:
            counter = 0
            points_logged = select(l for l in PasswordScoreLog if l.user == user)

            for point in points_logged:
                counter += point.points

            return counter


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
