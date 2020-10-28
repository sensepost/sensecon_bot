import requests
from loguru import logger
from pony import orm

from .base import BaseAction, EventType
from ..config import SCONWAR_TOKEN
from ..models import Sconwar as SconwarModel


class Sconwar(BaseAction):
    """
        Sconwar is an action to manage sconwar registrations
    """

    def should_stop(self) -> bool:
        return True

    def event_type(self) -> EventType:
        return EventType.Message

    def match(self) -> bool:
        return self.message.content.startswith('!sconwar register'.lower())

    async def execute(self):
        # loop guild members to id the sender
        async for member in self.client.guilds[0].fetch_members():
            if member.id != self.message.author.id:
                continue

            if not await self.is_verified(member):
                return

            with orm.db_session:
                user = SconwarModel.select(lambda c: c.userid == self.message.author.id).first()

                if user:  # we have a user, return the known token
                    await member.send(f'You have already registered for Sconwar! Your token is: {user.token}')
                    if self.message.guild:
                        await self.message.channel.send(f'<@{self.message.author.id}> check your dms')
                    return

                # we need a token, get and store it.

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

                user = SconwarModel(
                    userid=self.message.author.id,
                    token=r['uuid']
                )

                await member.send(f'Welcome to Sconwar! Your player token is (keep it safe): {user.token}')
                if self.message.guild:
                    await self.message.channel.send(f'<@{self.message.author.id}> check your dms')
