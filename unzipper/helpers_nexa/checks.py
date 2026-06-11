# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

import logging
from pyrogram import enums
from unzipper import unzip_client
from config import Config


async def check_log_channel():
    """
    FIX: This function uses async Pyrogram calls — must be async and awaited.
    """
    try:
        if not Config.LOGS_CHANNEL:
            logging.warning("No Log Channel ID is given!")
            return

        c_info = await unzip_client.get_chat(chat_id=Config.LOGS_CHANNEL)

        if c_info.type != enums.ChatType.CHANNEL:
            logging.warning("LOGS_CHANNEL is not a channel!")
            return
        if c_info.username is not None:
            logging.warning("LOGS_CHANNEL is not private!")
            return

        await unzip_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=(
                "`Unzipper-Bot has Successfully Started!`\n\n"
                "**Powered by @anujedits76**"
            )
        )
        logging.info("Log channel verified successfully.")

    except Exception as e:
        logging.warning(f"Error checking Log Channel: {e}")
