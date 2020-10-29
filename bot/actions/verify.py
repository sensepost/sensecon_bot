import re
import smtplib
from email.mime.text import MIMEText
from random import randint

from pony import orm
from pony.orm import desc
from  loguru import logger

from .base import BaseAction, EventType
from ..config import *
from ..discordoptions import EmojiRoleMap, DiscordRoles
from ..models import User


def send_mail(to_address, code):
    mail_server = smtplib.SMTP(EMAIL_SMTP, 587)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.login(EMAIL_USER, EMAIL_PASS)

    msg = MIMEText(
        f'Please send a direct message to the bot with !otp and '
        f'the following code to complete the registration. Code: {code}'
    )
    msg['Subject'] = "SenseCon Discord OTP code"
    msg['From'] = f"SenseCon Discord Server <{EMAIL_FROM}>"
    msg['To'] = to_address

    mail_server.sendmail(f'{EMAIL_FROM}', to_address, msg.as_string())
    mail_server.quit()


class Verify(BaseAction):
    """
        Sends an email to a user that owns an @orangecyberdefense email account.
        At least, tries to ;)
    """

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return True

    def match(self) -> bool:
        return self.message.content.startswith('!verify')

    async def execute(self):
        if '@orangecyberdefense.com' not in self.message.content.lower():
            await self.message.author.send('Verify syntax is `!verify hacker@orangecyberdefense.com`')
            return

        # loop guild members to id the sender
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            # ensure that the member has a country role
            has_flag = False
            for user_roles in member.roles:
                if user_roles.name in EmojiRoleMap.values():
                    has_flag = True

            if not has_flag:
                await self.message.author.send('Please ensure you have selected a country flag in the #lobby first.')
                return

            # if await self.is_verified(member, alert=False):
            #     await member.send('You are already verified! If it looks like it did not work, ping an admin.')
            #     # todo: maybe some sync work?
            #     return

            emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", self.message.content)

            if len(emails) <= 0:
                await member.send('I see what you are trying to do. Don\'t :)')
                return

            with orm.db_session:
                # user = User.select(lambda u: u.userid == self.message.author.id).first()
                #
                # if user and user.verified:
                #     await member.send(f'You have already registered with email: {user.email}')
                #     return

                otp = randint(10000, 99999)

                user = User(
                    userid=self.message.author.id,
                    email=emails[0],
                    otp=otp,
                    verified=False
                )

                logger.info(f'sending an email to {user.email}')
                send_mail(user.email, user.otp)

                await self.message.author.send(f'An email with an OTP has been sent to {user.email}.\n'
                                               f'Tell me what you got with `!otp <otp>` now.')


class Otp(BaseAction):
    """
        Verifies an OTP for a user.

        If you manage to figure out that we have an email parsing issue here,
        you can earn the Hacker challenge.
    """

    def event_type(self) -> EventType:
        return EventType.Message

    def should_stop(self) -> bool:
        return True

    def match(self) -> bool:
        return self.message.content.startswith('!otp')

    async def execute(self):
        # loop guild members to id the sender
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            with orm.db_session:
                user = User.select(lambda u: u.userid == self.message.author.id).order_by(desc(User.id)).first()

                if not user:
                    await member.send(f'Going a bit fast there! Try `!verify` first')
                    return

                otps = re.findall(r"(?<!\d)\d{5}(?!\d)", self.message.content)
                if len(otps) <= 0:
                    await member.send(f'OTP submission format is `!otp <value>`. eg: `!otp 31337`')
                    return

                if otps[0] != str(user.otp):
                    user.otp = 0
                    await member.send(f'Incorrect OTP, sorry. Please verify again '
                                      f'(we just unset the one you had in the backend, no bruting, sorry).')
                    return

                # update the db as a verified user
                user.otp = 0
                user.verified = True

                await self.grant_member_role(member, DiscordRoles.Verified, announce=False)
                await member.send('You have been verified.')

                # this is a challenge :P

                if '@orangecyberdefense.com' not in user.email:
                    await self.grant_member_role(member, DiscordRoles.Hacker)
