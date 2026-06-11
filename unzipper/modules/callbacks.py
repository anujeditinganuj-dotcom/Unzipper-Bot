# ===================================================================== #
#  Modified: Src-bot ButtonStyle + emoji + wallhaven back-to-home       #
# ===================================================================== #

import logging
from time import time
from shutil import rmtree
from os import makedirs, path

from config import Config
from aiohttp import ClientSession
from unzipper import unzip_client, Buttons
from unzipper.client.caching import USER_LANG

from pyrogram.types import CallbackQuery, InputMediaPhoto
from unzipper.database.cloud import GofileDB
from pyrogram.errors import ReplyMarkupTooLong
from unzipper.database.language import set_language
from unzipper.database.upload_mode import set_upload_mode

from unzipper.helpers_nexa.utils import (TimeFormatter, get_files,
                                         humanbytes, progress_for_pyrogram)
from unzipper.database.split_arc import add_split_arc_user, del_split_arc_user
from unzipper.lib.downloader import Downloader
from unzipper.lib.backup_tool import CloudBackup
from unzipper.lib.extractor import Extractor, ExtractionFailed

from unzipper.modules.user_utils import fetch_random_wallhaven_image
from unzipper.helpers_nexa.buttons import (
    E_STAR, E_ROCKET, E_GREEN, E_BOLT, E_LOCK, E_STATS, E_ARROW
)


@unzip_client.on_callback_query()
@unzip_client.handle_query
async def unzipper_cb(client, query: CallbackQuery, texts):
    qdat = query.data

    # ── Home / Back ───────────────────────────────────────────────────
    if qdat == "megoinhome":
        bot_me  = await client.get_me()
        mention = query.from_user.mention
        caption = (
            f"<b>{E_STAR} Hello {mention},</b>\n"
            f"<b>{E_ROCKET} I am <a href='https://t.me/{bot_me.username}'>{bot_me.first_name}</a></b>\n"
            f"<i>Your Ultimate Archive Extractor Bot.</i>\n"
            f"<blockquote>"
            f"<b>{E_GREEN} System Status: Online</b>\n"
            f"<b>{E_BOLT} Supports: ZIP, RAR, 7Z, TAR & more</b>\n"
            f"<b>{E_LOCK} Secure Processing</b>\n"
            f"<b>{E_STATS} Uptime: 99.9% Guaranteed</b>"
            f"</blockquote>\n"
            f"<b>{E_ARROW} Select an option below to get started:</b>"
        )
        photo_url = await fetch_random_wallhaven_image()
        try:
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(media=photo_url, caption=caption),
                reply_markup=Buttons.START
            )
        except Exception:
            try:
                await query.edit_message_caption(
                    caption=caption,
                    reply_markup=Buttons.START,
                    parse_mode="html"
                )
            except Exception:
                pass

    # ── Help ──────────────────────────────────────────────────────────
    elif qdat == "helpcallback":
        await query.edit_message_caption(
            caption=texts["help_head"],
            reply_markup=Buttons.HELP,
            parse_mode="html"
        )

    elif qdat == "extracthelp":
        await query.edit_message_caption(
            caption=texts["help_extract"],
            reply_markup=Buttons.HELP_BACK,
            parse_mode="html"
        )

    elif qdat == "upmodhelp":
        await query.edit_message_caption(
            caption=texts["help_upmode"],
            reply_markup=Buttons.HELP_BACK,
            parse_mode="html"
        )

    elif qdat == "backuphelp":
        await query.edit_message_caption(
            caption=texts["help_backup"],
            reply_markup=Buttons.HELP_BACK,
            parse_mode="html"
        )

    elif qdat == "thumbhelp":
        await query.edit_message_caption(
            caption=texts["help_thumb"],
            reply_markup=Buttons.HELP_BACK,
            parse_mode="html"
        )

    elif qdat == "langhelp":
        await query.edit_message_caption(
            caption=texts["help_lang"],
            reply_markup=Buttons.HELP_BACK,
            parse_mode="html"
        )

    elif qdat == "aboutcallback":
        await query.edit_message_caption(
            caption=texts["about"].format(unzip_client.version),
            reply_markup=Buttons.BACK,
            parse_mode="html"
        )

    # ── Extract ───────────────────────────────────────────────────────
    elif qdat.startswith("extract_file"):
        splitted_data = qdat.split("|")
        user_id       = query.from_user.id
        r_message     = query.message.reply_to_message
        arc_name      = ""
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"

        try:
            makedirs(download_path, exist_ok=True)  # FIX: exist_ok

            if splitted_data[1] == "url":
                url = r_message.text
                async with ClientSession() as ses:
                    cleng = (await ses.head(url)).headers.get("Content-Length")
                    fsize = humanbytes(int(cleng)) if cleng else "undefined"
                await unzip_client.send_message(
                    Config.LOGS_CHANNEL,
                    texts["log"].format(user_id, "N/A", "N/A", url, fsize)
                )
                s_time   = time()
                arc_name = f"{download_path}/archive_from_{user_id}_{path.basename(url)}"
                await Downloader().download(url, arc_name, query.message)
                e_time   = time()

            elif splitted_data[1] == "tg_file":
                rdoc  = r_message.document
                rchat = r_message.forward_from_chat
                await r_message.copy(
                    Config.LOGS_CHANNEL,
                    texts["log"].format(
                        user_id,
                        rchat.title if rchat else "N/A",
                        rchat.id   if rchat else "N/A",
                        rdoc.file_name,
                        humanbytes(rdoc.file_size)
                    )
                )
                s_time   = time()
                arc_name = f"{download_path}/archive_from_{user_id}_{rdoc.file_name}"
                await r_message.download(
                    file_name=arc_name,
                    progress=progress_for_pyrogram,
                    progress_args=("**Trying to Download!** \n", query.message, s_time)
                )
                e_time = time()
            else:
                return await unzip_client.answer_query(
                    query,
                    "Can't Find Details! Please contact support group!",
                    True   # FIX: was answer_only=True which doesn't exist
                )

            await unzip_client.answer_query(
                query,
                texts["ok_download"].format(arc_name, TimeFormatter(round(e_time - s_time) * 1000))
            )

            arc_ext = path.splitext(arc_name)[1]
            if arc_ext.replace(".", "").isnumeric():
                password = ""
                if splitted_data[2] == "with_pass":
                    password = (await unzip_client.ask(
                        query.message.chat.id, texts["ask_password"]
                    )).text
                await unzip_client.answer_query(query, texts["alert_splitted_arc"])
                await add_split_arc_user(user_id, arc_name, password)
                return

            exter = Extractor()
            if splitted_data[2] == "with_pass":
                password  = (await unzip_client.ask(
                    query.message.chat.id, texts["ask_password"]
                )).text
                ext_s     = time()
                await exter.extract(arc_name, ext_files_dir, password)
                ext_e     = time()
            else:
                ext_s = time()
                await exter.extract(arc_name, ext_files_dir)
                ext_e = time()

            await unzip_client.answer_query(
                query,
                texts["ok_extract"].format(TimeFormatter(round(ext_e - ext_s) * 1000))
            )

            files      = await get_files(ext_files_dir)
            i_e_buttons = await Buttons.make_files_keyboard(files, user_id, query.message.chat.id)
            try:
                await unzip_client.answer_query(query, texts["select_files"], reply_markup=i_e_buttons)
            except ReplyMarkupTooLong:
                i_e_buttons = await Buttons.make_files_keyboard(
                    files, user_id, query.message.chat.id, False
                )
                await unzip_client.answer_query(query, texts["select_files"], reply_markup=i_e_buttons)

        except ExtractionFailed:
            await unzip_client.answer_query(query, texts["failed_extract"])
        except BaseException as e:
            try:
                await unzip_client.answer_query(query, texts["failed_main"].format(e))
                rmtree(download_path, ignore_errors=True)
            except Exception as er:
                logging.warning(er)

    # ── Upload single file ────────────────────────────────────────────
    elif qdat.startswith("ext_f"):
        spl_data  = qdat.split("|")
        # FIX: spl_data = ["ext_f", user_id, chat_id, file_num]
        uid       = int(spl_data[1])
        chat_id   = int(spl_data[2])   # FIX: cast to int
        file_num  = int(spl_data[3])

        file_path = f"{Config.DOWNLOAD_LOCATION}/{uid}/extracted"
        files     = await get_files(file_path)

        if not files:
            dl_path = f"{Config.DOWNLOAD_LOCATION}/{uid}"
            if path.isdir(dl_path):
                rmtree(dl_path, ignore_errors=True)
            return await unzip_client.answer_query(query, texts["alert_empty_files"])

        await unzip_client.answer_query(query, texts["alert_sending_file"], True)
        await unzip_client.send_file(chat_id, files[file_num], query, texts["this_lang"])

        await unzip_client.answer_query(query, texts["refreshing"])
        files = await get_files(file_path)
        if not files:
            try:
                rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}", ignore_errors=True)
            except Exception:
                pass
            return await unzip_client.answer_query(query, texts["ok_upload_basic"])

        i_e_buttons = await Buttons.make_files_keyboard(files, uid, chat_id)
        try:
            await unzip_client.answer_query(query, texts["select_files"], reply_markup=i_e_buttons)
        except ReplyMarkupTooLong:
            i_e_buttons = await Buttons.make_files_keyboard(files, uid, chat_id, False)
            await unzip_client.answer_query(query, texts["select_files"], reply_markup=i_e_buttons)

    # ── Upload all files ──────────────────────────────────────────────
    elif qdat.startswith("ext_a"):
        spl_data = qdat.split("|")
        uid      = int(spl_data[1])
        chat_id  = int(spl_data[2])   # FIX: cast to int

        file_path = f"{Config.DOWNLOAD_LOCATION}/{uid}/extracted"
        paths     = await get_files(file_path)

        if not paths:
            if path.isdir(f"{Config.DOWNLOAD_LOCATION}/{uid}"):
                rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}", ignore_errors=True)
            return await unzip_client.answer_query(query, texts["alert_empty_files"])

        await unzip_client.answer_query(query, texts["alert_sending_files"], True)
        for file in paths:
            await unzip_client.send_file(chat_id, file, query, texts["this_lang"], True)

        await unzip_client.answer_query(query, texts["ok_upload_basic"])
        rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}", ignore_errors=True)

    # ── Upload mode ───────────────────────────────────────────────────
    elif qdat.startswith("set_mode"):
        mode = qdat.split("|")[1]
        await set_upload_mode(query.from_user.id, mode)
        await unzip_client.answer_query(query, texts["changed_upmode"].format(mode))

    # ── Language ──────────────────────────────────────────────────────
    elif qdat.startswith("set_lang"):
        qlang = qdat.split("|")[1]
        chid  = query.message.chat.id
        USER_LANG[chid] = qlang
        await set_language(chid, qlang)
        await unzip_client.answer_query(query, texts["changed_lang"].format(qlang))

    # ── Gofile settings ───────────────────────────────────────────────
    elif qdat.startswith("gf_setting"):
        gf   = GofileDB(query.from_user.id)
        mode = qdat.split("-")[1]
        if mode == "set":
            tkn = await unzip_client.ask(query.message.chat.id, texts["ask_gofile_token"])
            await gf.save_token(tkn.text)
            await tkn.delete()
        elif mode == "del":
            await gf.del_token()
        elif mode == "get":
            return await unzip_client.answer_query(
                query, texts["gofile_token"].format(await gf.get_token())
            )
        await unzip_client.answer_query(query, "**Done ✅!**")

    # ── Cloud backup ──────────────────────────────────────────────────
    elif qdat.startswith("cloudbackup"):
        clb = CloudBackup(query.from_user.id)
        to  = qdat.split("|")[1]
        if to == "gofile":
            await unzip_client.answer_query(query, texts["alert_uploading_to_gofile"])
            glnk = await clb.gofile_backup()
            await unzip_client.answer_query(
                query,
                texts["ok_backup"].format(glnk),
                reply_markup=await Buttons.make_button("Gofile link 🔗", url=glnk)
            )

    # ── Cancel / nobully ──────────────────────────────────────────────
    elif qdat == "cancel_dis":
        await del_split_arc_user(query.from_user.id)
        try:
            rmtree(f"{Config.DOWNLOAD_LOCATION}/{query.from_user.id}", ignore_errors=True)
        except Exception:
            pass
        await unzip_client.answer_query(query, texts["canceled"].format("Process cancelled"))

    elif qdat == "nobully":
        await unzip_client.answer_query(query, texts["ok_wont_delete"])
