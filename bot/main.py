import sys

import click
from loguru import logger
from pony import orm

from .actions import sconwar, country, challenges, verify
from .client import client
from .models import db


@click.command()
@click.option('--debug', is_flag=True, default=False, help='enable debug logs')
@click.option('--db-path', default='db.sqlite', help='sqlite db path')
def cli(debug, db_path):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    db.bind(provider='sqlite', filename=db_path, create_db=True)
    if debug:
        orm.set_sql_debug(True)
    db.generate_mapping(create_tables=True)

    client.add_action(challenges.MexicanWave())
    client.add_action(challenges.Sneaky())
    client.add_action(challenges.Beautiful())
    client.add_action(challenges.EavesDropper())
    client.add_action(country.CountryFlagAdd())
    client.add_action(country.CountryFlagRemove())

    client.add_action(sconwar.Sconwar())
    client.add_action(verify.Verify())
    client.add_action(verify.Otp())

    client.run()


if __name__ == '__main__':
    cli()
