# discord_bot_challenge

A simple Discord bot created for [SenseCon](https://sensepost.com/blog/2020/sensecon-2020-ex-post-facto/) 2020.

## running

This bot makes use of a sqlite database. You can "create" it by just running `touch db.sqlite`.

### without docker

Run the both with `python3 -m bot.main` or install as a symlink with `pip3 install --editable .` and run with `discord-bot`.

### with docker

For docker, use `docker run --rm -it -v $(pwd)/db.sqlite:/db.sqlite discord-bot:local` after a `docker build -t discord-bot:local .`.

Otherwise, simply do a `docker-compose up -d`.
