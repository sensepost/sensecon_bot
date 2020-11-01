FROM python:3.8-buster

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

ADD . /app

RUN cd /app && pip3 install .

ENTRYPOINT [ "discord-bot", "--db-path", "/db.sqlite" ]
