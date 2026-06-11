# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

import logging
import asyncio
from os import makedirs, path
from config import Config
from .server import keep_alive

# FIX: 'import *' is only allowed at module level, not inside a function.
# Moved here from inside main() to prevent "SyntaxError: import * only
# allowed at module level" at runtime.
from unzipper.modules import admin, callbacks, extract, settings, user_utils  # noqa: F401


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
