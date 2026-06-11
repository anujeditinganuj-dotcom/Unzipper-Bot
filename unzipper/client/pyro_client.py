# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

import logging
from time import time
from asyncio import sleep
from typing import Callable
from os import path, remove, stat

from gofile2 import Gofile
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, Message

from config import Config
from .caching import STRINGS
from unzipper import Buttons
from unzipper.database.language import get_language
from unzipper.database.upload_mode import get_upload_mode
from unzipper.helpers_nexa.utils import (
    TimeFormatter,
    progress_for_pyrogram,
    rm_mark_chars,
    run_shell_cmds_async   # FIX: use async version
)


class UnzipperBot(Client):

    version = "v1.0.2"

    def __init__(self):
        super().__init__(
            "UnzipperBot",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="unzipper.modules"),
            sleep_threshold=10
        )

    # -------------- DECORATORS -------------- #

    def handle_erros(self, func: Callable) -> Callable:
        async def decorator(client: Client, message: Message):
            lang = await get_language(message.chat.id)
            try:
                await self.check_user(message)
                return await func(client, message, STRINGS[lang])
            except Exception as e:
                logging.warning(e)
                try:
                    await self.send_message(
                        message.chat.id,
                        STRINGS[lang]["failed_main"].format(e)
                    )
                except Exception:
                    pass
        return decorator

    def handle_query(self, func: Callable) -> Callable:
        async def decorator(client: Client, query: CallbackQuery):
            lang = await get_language(query.message.chat.id)
            try:
                await func(client, query, STRINGS[lang])
            except Exception as e:
                logging.warning(e)
                try:
                    await self.send_message(
                        query.message.chat.id,
                        STRINGS[lang]["failed_main"].format(e)
                    )
                except Exception:
                    pass
        return decorator

    # -------------- SEND FILE -------------- #

    async def send_file(self, c_id: int, doc_f: str, query: CallbackQuery,
                        lang: str = "en", del_status: bool = False):
        sthumb = None
        try:
            cum       = await get_upload_mode(c_id)
            file_size = stat(doc_f).st_size

            # Large file → Gofile
            if file_size > Config.TG_MAX_SIZE:
                upmsg = await self.send_message(c_id, text=STRINGS[lang]["alert_file_too_large"])
                try:
                    ga   = await Gofile.initialize()
                    gfio = await ga.upload(doc_f)
                    await upmsg.edit(
                        "**Uploaded to GoFile 👇**",
                        reply_markup=await Buttons.make_button("Download 🔗", url=gfio["downloadPage"])
                    )
                except Exception as e:
                    logging.warning(f"Gofile error: {e}")
                    await upmsg.edit("Upload failed 😔")
                if path.exists(doc_f):
                    remove(doc_f)
                return

            tgupmsg = await self.send_message(c_id, STRINGS[lang]["processing"])
            stm     = time()

            # Video upload
            if cum == "video":
                sthumb = await self.get_or_gen_thumb(c_id, doc_f, True)

                vid_duration = await run_shell_cmds_async(
                    f'ffprobe -v error -show_entries format=duration '
                    f'-of default=noprint_wrappers=1:nokey=1 "{doc_f}"'
                )

                await self.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption="**Extracted by bot**",
                    duration=int(float(vid_duration)) if vid_duration.strip() else 0,
                    thumb=sthumb,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading...", tgupmsg, stm)
                )

            # Document upload
            else:
                sthumb = await self.get_or_gen_thumb(c_id, doc_f)
                await self.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    caption="**Extracted by bot**",
                    thumb=sthumb,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading...", tgupmsg, stm)
                )

            etm = time()

            try:
                await tgupmsg.edit(
                    STRINGS[lang]["ok_upload"].format(
                        path.basename(doc_f),
                        TimeFormatter(round(etm - stm) * 1000)
                    )
                )
            except Exception:
                await tgupmsg.delete()

            # Cleanup
            try:
                await sleep(1)
                if path.exists(doc_f):
                    remove(doc_f)
                if sthumb and path.exists(sthumb):
                    remove(sthumb)
            except Exception as e:
                logging.warning(f"Cleanup error: {e}")

        except FloodWait as f:
            # FIX: .value for new pyrogram, .x for old
            wait = f.value if hasattr(f, "value") else f.x
            await sleep(wait)
            return await self.send_file(c_id, doc_f, query, lang, del_status)

        except FileNotFoundError:
            return await self.answer_query(query, "File not found ❌", True)

        except Exception as e:
            logging.warning(e)
            await self.answer_query(query, f"Error: {e}", True)

    # -------------- ANSWER QUERY -------------- #

    async def answer_query(self, query: CallbackQuery, text: str,
                           alert: bool = False, *args, **kwargs):
        try:
            if alert:
                await query.answer(await rm_mark_chars(text), show_alert=True)
            else:
                await query.message.edit(text, *args, **kwargs)
        except Exception:
            try:
                await query.message.delete()
            except Exception:
                pass
            try:
                await self.send_message(query.message.chat.id, text, *args, **kwargs)
            except Exception:
                pass
