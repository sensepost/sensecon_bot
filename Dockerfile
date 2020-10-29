FROM python:3.8-buster

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "-m", "bot.main", "--db-path", "/db.sqlite" ]
