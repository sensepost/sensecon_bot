# discord_bot_challenge

Run with `python3 -m bot.main` or install as a symlink with `pip3 install --editable .` and run with `discord-bot`.

For docker, use `docker run --rm -it -v $(pwd)/db.sqlite:/db.sqlite discord-bot:local` after a `docker build -t discord-bot:local .`.

Otherwise, simply do a `docker-compose up -d`.
