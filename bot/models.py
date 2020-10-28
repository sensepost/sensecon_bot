from pony.orm import Database, Required

db = Database()


class User(db.Entity):
    """
        A Discord bot user, tied to an email account
    """

    userid = Required(int, size=64, index=True)
    email = Required(str, index=True)
    otp = Required(int)
    verified = Required(bool)


class Sconwar(db.Entity):
    """
        Sconwar token storage
    """

    userid = Required(int, size=64, index=True)
    token = Required(str)
