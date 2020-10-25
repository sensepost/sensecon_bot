FROM linuxserver/ffmpeg:latest

RUN apt update && apt install -y python3-pip

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "./main.py" ]
