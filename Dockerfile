FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    zstd p7zip-full gcc ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip setuptools --break-system-packages
RUN mkdir /app/
WORKDIR /app/
COPY . /app/
RUN pip3 install -U -r requirements.txt --break-system-packages
CMD bash start.sh
