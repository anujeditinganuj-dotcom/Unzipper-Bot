# Copyright (c) 2022 Itz-fork

import os

class Config(object):
    # Mandatory
    APP_ID       = int(os.environ.get("APP_ID", "34446649"))
    API_HASH     = os.environ.get("API_HASH", "8dc570c08d8e35e88fb9bfc73c65d7fa")
    BOT_TOKEN    = os.environ.get("BOT_TOKEN", "8701067336:AAEwGUgQ1z2OcTQK2x0sMOs1bcDdSbG7Dvs")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", "-1003951808679"))
    BOT_OWNER    = int(os.environ.get("BOT_OWNER", "7892805795"))
    MONGODB_URL  = os.environ.get("MONGODB_URL", "mongodb+srv://Anujedit:Anujedit@cluster0.7cs2nhd.mongodb.net/?appName=Cluster0")
    GOFILE_TOKEN = os.environ.get("GOFILE_TOKEN", "dtTUYSgS85ipBgOyohzyfbZ99nhyZLcd")

    # Optional
    MAX_DOWNLOAD_SIZE = (
        int(os.environ["MAX_DOWNLOAD_SIZE"])
        if os.environ.get("MAX_DOWNLOAD_SIZE")
        else 10737418240  # 10 GB default
    )

    # Use absolute path so it works regardless of cwd
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_LOCATION = os.path.join(_BASE_DIR, "Anujedits76")

    # Constants
    TG_MAX_SIZE = 2040108421
    CHUNK_SIZE  = 1024 * 6
