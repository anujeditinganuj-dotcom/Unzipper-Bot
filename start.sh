#!/usr/bin/bash

VERSION="v1.0"
echo "
    ||| Unzipper Bot - $VERSION |||

Copyright (c) 2022 Itz-fork

--> Join @anujedits76
--> Follow Itz-fork on Github

"

# Install system dependencies if not present
if ! command -v 7z &> /dev/null; then
    echo ">> Installing p7zip-full..."
    apt-get update -qq && apt-get install -y -qq p7zip-full
fi

if ! command -v zstd &> /dev/null; then
    echo ">> Installing zstd..."
    apt-get install -y -qq zstd
fi

if ! command -v ffmpeg &> /dev/null; then
    echo ">> Installing ffmpeg..."
    apt-get install -y -qq ffmpeg
fi

python3 -m unzipper
