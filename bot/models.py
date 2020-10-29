from datetime import datetime

from pony.orm import Database, Required, Optional, Set

db = Database()


class User(db.Entity):
    """
        A Discord bot user, tied to an email account
    """

    userid = Required(int, size=64, index=True)
    email = Required(str, index=True)
    otp = Required(int)
    verified = Required(bool)

    # sconwar challenge
    sconwar_token = Optional("Sconwar")

    # password challenge
    password_score_log = Optional("PasswordScoreLog")
    passwords_cracked = Set("Password")


class Sconwar(db.Entity):
    """
        Sconwar token storage
    """

    user = Required(User)
    token = Required(str)


class Password(db.Entity):
    """
        Password is a password
    """

    user = Set(User)
    challenge = Required(int)
    cleartext = Required(str)
    value = Required(int)


class PasswordScoreLog(db.Entity):
    """
        A log of cracked passwords
    """

    user = Required(User)
    # password = Set(Password)
    clear = Required(str)
    points = Required(int)
    submitted = Required(datetime, default=datetime.utcnow())
