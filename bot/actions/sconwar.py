import requests
from loguru import logger
from pony import orm

from .base import BaseAction, EventType
from ..config import SCONWAR_TOKEN
from ..discordoptions import DiscordChannels
from ..models import User, Sconwar as SconwarToken


class Sconwar(BaseAction):
    """
        Sconwar is an action to manage sconwar registrations
    """

    def should_stop(self) -> bool:
        return True

    def event_type(self) -> EventType:
        return EventType.Message

    def match(self) -> bool:
        return self.message.content.startswith('!sconwar register')

    async def execute(self):
        # loop guild members to id the sender
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

            with orm.db_session:
                user = User.select(lambda c: c.userid == self.message.author.id).first()

                if not user:
                    logger.warning(f'user {member.nick if member.nick else member.display_name} tried to '
                                   f'register for sconwar before verifying (no db user)')
                    await member.send(f'make sure you have verified first before we do anything, please.')
                    return

                if user.sconwar_token:
                    await member.send(
                        f'You have already registered for Sconwar! Your token is: `{user.sconwar_token.token}`')
                    if self.message.guild:
                        await self.message.channel.send(f'<@{self.message.author.id}> check your dms')
                    return

                logger.info('getting a new player token from sconwar')

                headers = {
                    'accept': 'application/json',
                    'token': SCONWAR_TOKEN,  # <-- sekret
                    'Content-Type': 'application/json',
                }

                r = requests.post('https://api.sconwar.com/api/player/register', headers=headers, json={
                    "name": member.nick if member.nick else member.name
                }).json()

                if 'created' not in r:
                    logger.error(f'failed to request a sconwar token. response was {r}')
                    await member.send(f'failed to get you a token. ask an admin to help!')
                    return

                SconwarToken(user=user, token=r['uuid'])

                await member.send(f'Welcome to Sconwar! Your player token is '
                                  f'(keep it safe): `{user.sconwar_token.token}`')
                await self.send_channel_message(f'Look out! <@{self.message.author.id}> has joined sconwar!',
                                                DiscordChannels.Sconwar)
                if self.message.guild:
                    await self.message.channel.send(f'<@{self.message.author.id}> check your dms')
