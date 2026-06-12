# Copyright (c) 2022 Itz-fork

import os

class Config(object):
    # Mandatory
    APP_ID       = int(os.environ.get("APP_ID", "37476811"))
    API_HASH     = os.environ.get("API_HASH", "7aa60670b871050820086c6267371ee6")
    BOT_TOKEN    = os.environ.get("BOT_TOKEN", "8015464564:AAFe6QCyYpfSWPGbwih_u_XejaDLcho1KOI")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", "-1003955674028"))
    BOT_OWNER = int(str(os.environ.get("BOT_OWNER", "8730393744")).strip())
    MONGODB_URL  = os.environ.get("MONGODB_URL", "mongodb+srv://Anujedit:Anujedit@cluster0.7cs2nhd.mongodb.net/?appName=Cluster0")
    GOFILE_TOKEN = os.environ.get("GOFILE_TOKEN", "dtTUYSgS85ipBgOyohzyfbZ99nhyZLcd")

    # Optional
    MAX_DOWNLOAD_SIZE = (
        int(os.environ["MAX_DOWNLOAD_SIZE"])
        if os.environ.get("MAX_DOWNLOAD_SIZE")
        else 10737418240  # 10 GB default
    )

    # Use /tmp for Render/cloud compatibility (writable on all platforms)
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "/tmp/Anujedits76")

    # Constants
    TG_MAX_SIZE = 2040108421
    CHUNK_SIZE  = 1024 * 6
