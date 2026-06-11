FROM archlinux:latest

RUN pacman -Syyu --noconfirm
RUN pacman -S --noconfirm python-pip zstd p7zip gcc ffmpeg
RUN pip3 install -U pip --break-system-packages
RUN mkdir /app/
WORKDIR /app/
COPY . /app/
RUN pip3 install -U setuptools --break-system-packages
RUN pip3 install -U -r requirements.txt --break-system-packages
CMD bash start.sh
