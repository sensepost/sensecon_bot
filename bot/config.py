import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SCONWAR_TOKEN = os.getenv('SCONWAR_TOKEN')

EMAIL_SMTP = os.getenv('EMAIL_SMTP')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_FROM = os.getenv('EMAIL_FROM')
