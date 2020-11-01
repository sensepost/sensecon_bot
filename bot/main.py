import sys

import click
from loguru import logger
from pony import orm

from .actions import sconwar, country, challenges, verify, password, admin
from .client import client
from .models import db


@click.command()
@click.option('--debug', is_flag=True, default=False, help='enable debug logs')
@click.option('--db-debug', is_flag=True, default=False, help='enable db debug logs')
@click.option('--db-path', default='db.sqlite', help='sqlite db path')
def cli(debug, db_debug, db_path):
    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.info('preparing database config')
    db.bind(provider='sqlite', filename=db_path, create_db=True)
    if db_debug:
        orm.set_sql_debug(True)
    db.generate_mapping(create_tables=True)

    logger.info('loading actions')
    client.add_action(challenges.MexicanWave())
    client.add_action(challenges.Sneaky())
    client.add_action(challenges.Beautiful())
    client.add_action(challenges.EavesDropper())

    client.add_action(password.PasswordDownload())
    client.add_action(password.PasswordUpload())
    client.add_action(password.PasswordScore())

    client.add_action(country.CountryFlagAdd())
    client.add_action(country.CountryFlagRemove())

    client.add_action(sconwar.Sconwar())

    client.add_action(verify.Verify())
    client.add_action(verify.Otp())

    client.add_action(admin.SendMessage())

    logger.info('booting bot')
    client.run()


if __name__ == '__main__':
    cli()
