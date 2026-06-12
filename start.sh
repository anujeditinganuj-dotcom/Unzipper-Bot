#!/usr/bin/bash

VERSION="v1.0"
echo "
    ||| Unzipper Bot - $VERSION |||

Copyright (c) 2026 Anuj

--> Join @anujedits76
--> Follow Anuj on Github

"

# Install system dependencies if not present
if ! command -v 7z &> /dev/null; then
    echo ">> Installing p7zip..."
    if command -v pkg &> /dev/null; then
        pkg install -y p7zip
    elif command -v apt-get &> /dev/null; then
        apt-get update -qq && apt-get install -y -qq p7zip-full
    else
        echo "!! Could not find pkg or apt-get to install p7zip. Please install it manually."
    fi
fi

if ! command -v zstd &> /dev/null; then
    echo ">> Installing zstd..."
    if command -v pkg &> /dev/null; then
        pkg install -y zstd
    elif command -v apt-get &> /dev/null; then
        apt-get update -qq && apt-get install -y -qq zstd
    else
        echo "!! Could not find pkg or apt-get to install zstd. Please install it manually."
    fi
fi

if ! command -v ffmpeg &> /dev/null; then
    echo ">> Installing ffmpeg..."
    if command -v pkg &> /dev/null; then
        pkg install -y ffmpeg
    elif command -v apt-get &> /dev/null; then
        apt-get install -y -qq ffmpeg
    else
        echo "!! Could not find pkg or apt-get to install ffmpeg. Please install it manually."
    fi
fi

python3 -m unzipper
