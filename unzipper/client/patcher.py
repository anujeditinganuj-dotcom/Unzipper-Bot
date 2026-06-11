# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

import logging
import os
from os import path, remove

from .pyro_client import UnzipperBot
from unzipper.database.thumbnail import get_thumbnail
from unzipper.helpers_nexa.utils import run_shell_cmds_async   # FIX: async version
from unzipper.database.users import add_user, is_user_in_db, is_user_in_bdb
from config import Config


class PatchMethods:
    def __init__(self) -> None:
        super().__init__()

    async def check_user(self: UnzipperBot, message):
        """Register new users and block banned ones."""
        try:
            # FIX: message.from_user can be None in channels
            if not message.from_user:
                return
            user_id = int(message.from_user.id)

            # Ban check
            if await is_user_in_bdb(user_id):
                await message.reply("**Sorry You're Banned!**\n\nReport this at @anujedits76")
                raise Exception("User Banned")

            # DB registration
            if not await is_user_in_db(user_id):
                await add_user(user_id)

                if getattr(Config, "LOGS_CHANNEL", None):
                    try:
                        await self.send_message(
                            chat_id=Config.LOGS_CHANNEL,
                            text=(
                                "**#NEW_USER 🎙**\n\n"
                                f"**User:** {message.from_user.mention}\n"
                                f"**ID:** `{user_id}`\n"
                                f"**Profile:** [Click](tg://user?id={user_id})"
                            ),
                            disable_web_page_preview=True
                        )
                    except Exception as e:
                        logging.warning(f"Log send failed: {e}")

        except Exception as e:
            logging.warning(f"check_user error: {e}")
            raise  # re-raise so handle_erros decorator sees it

    # -------------- THUMBNAIL -------------- #

    async def get_or_gen_thumb(self: UnzipperBot, uid: int,
                               doc_f: str, isvid: bool = False):
        try:
            dbthumb = await get_thumbnail(int(uid), True)
            if dbthumb:
                return dbthumb

            if isvid:
                os.makedirs("Dump", exist_ok=True)
                thmb_pth = f"Dump/thumbnail_{path.basename(doc_f)}.jpg"

                if path.exists(thmb_pth):
                    remove(thmb_pth)

                # FIX: use async version
                await run_shell_cmds_async(
                    f'ffmpeg -ss 00:00:01.00 -i "{doc_f}" '
                    f'-vf "scale=320:320:force_original_aspect_ratio=decrease" '
                    f'-vframes 1 "{thmb_pth}"'
                )

                if path.exists(thmb_pth):
                    return thmb_pth

            return None

        except Exception as e:
            logging.warning(f"Thumbnail error: {e}")
            return None


class UserIsBanned(Exception):
    def __init__(self) -> None:
        super().__init__("You're banned from using this bot!")


def init_patch():
    """Apply PatchMethods onto UnzipperBot at runtime."""
    for key, val in PatchMethods.__dict__.items():
        if not key.startswith("__"):
            setattr(UnzipperBot, key, val)
