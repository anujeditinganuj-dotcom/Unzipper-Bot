# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

import logging
import asyncio
from os import makedirs, path
from config import Config
from .server import keep_alive

# NOTE: Do NOT manually import unzipper.modules here.
# Pyrogram's plugins=dict(root="unzipper/modules") in UnzipperBot.__init__
# already loads all modules automatically. Importing them again causes
# every handler to register TWICE → duplicate tasks → bot crashes.


async def main():
    # Start the Flask keep-alive server (in a background thread)
    keep_alive()

    # Ensure download directory exists
    logging.info(" >> Checking download location...")
    if not path.isdir(Config.DOWNLOAD_LOCATION):
        makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)

    # Patch extra methods onto UnzipperBot
    logging.info(" >> Applying custom methods...")
    from .client import init_patch
    init_patch()

    # Import client and start (modules already imported above)
    logging.info(" >> Starting client...")
    from unzipper import unzip_client

    await unzip_client.start()

    # Register custom listener middleware (pyromod replacement)
    logging.info(" >> Registering message listener middleware...")
    from unzipper.client.listener import resolve_listener
    from pyrogram import filters as _filters

    @unzip_client.on_message(_filters.private & ~_filters.command(
        ["start", "help", "mode", "setmode", "lang", "set_lang",
         "gofile", "gfsets", "save", "set_thumb", "thget", "get_thumb",
         "thdel", "del_thumb", "backup", "clean", "done", "stats",
         "ban", "unban", "broadcast"]
    ), group=-1)
    async def _listener_middleware(client, message):
        resolve_listener(message.chat.id, message)

    # Warm the language cache from DB (runs as background task)
    logging.info(" >> Loading language cache from DB...")
    from unzipper.client.caching import update_languages_cache
    update_languages_cache()

    # Verify log channel (async)
    logging.info(" >> Checking Log Channel...")
    from .helpers_nexa.checks import check_log_channel
    await check_log_channel()

    logging.info("Bot is active! Join @anujedits76")

    from pyrogram import idle
    await idle()


if __name__ == "__main__":
    asyncio.run(main())
