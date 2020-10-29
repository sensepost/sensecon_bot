from typing import List

import discord
from loguru import logger

from .actions.base import BaseAction, EventType
from .config import TOKEN

intents = discord.Intents.default()
intents.members = True

dc = discord.Client(intents=intents)


class Client(object):
    """
        Client is the discord client wrapper for out bot
    """

    actions: List[BaseAction]
    discord: discord.client.Client

    def __init__(self, d):
        self.discord = d
        self.actions = []

    def add_action(self, action: BaseAction):
        """
            Appends an action to the known actions list

            :param action:
            :return:
        """
        self.actions.append(action)

    @staticmethod
    def run():
        """
            Runs the bot

            :return:
        """

        dc.run(TOKEN)

    async def run_actions(self, event: EventType, **kwargs):
        """
            Runs the actions we have registered for an event type.

            **kwargs should be (with client always set):
                client, message, payload

            :param event:
            :param kwargs:
            :return:
        """

        # extract options to be passed to context setting
        c, m, p = kwargs.pop('client'), kwargs.pop('message', None), kwargs.pop('payload', None)

        for action in self.actions:
            if action.event_type() != event:
                continue

            action.set_context(client=c, message=m, payload=p)
            if not action.match():
                continue

            logger.info(f'matched the {action} action for event {event}')
            await action.execute()

            if action.should_stop():
                logger.debug(f'should stop triggered for action {action}')
                break


# this section details some discord specific events that need to be registered

@dc.event
async def on_message(message):
    logger.debug(f'reacting to on_message: {message}')
    await client.run_actions(EventType.Message, client=dc, message=message)


@dc.event
async def on_raw_reaction_add(payload):
    logger.debug(f'reacting to on_raw_reaction_add: {payload}')
    await client.run_actions(EventType.RawReactionAdd, client=dc, payload=payload)


@dc.event
async def on_raw_reaction_remove(payload):
    logger.debug(f'reacting to on_raw_reaction_remove: {payload}')
    await client.run_actions(EventType.RawReactionRemove, client=dc, payload=payload)


@dc.event
async def on_raw_message_edit(payload):
    logger.debug(f'reacting to on_raw_message_edit: {payload}')
    await client.run_actions(EventType.MessageEdit, client=dc, payload=payload)


@dc.event
async def on_voice_state_update(member, before, after):
    logger.debug(f'reacting to on_voice_state_update: (not used: {member}, {before}, {after})')
    await client.run_actions(EventType.VoiceStateUpdate, client=dc)


client = Client(dc)
