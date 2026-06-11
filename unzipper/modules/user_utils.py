# ===================================================================== #
#  Modified: Wallhaven random photo + text on /start  (Src-bot style)  #
# ===================================================================== #

import random
import logging
import aiohttp
from os import path, remove
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from unzipper import unzip_client, Buttons
from unzipper.database.thumbnail import save_thumbnail, get_thumbnail, del_thumbnail
from unzipper.client.caching import STRINGS
from unzipper.database.language import get_language
from unzipper.helpers_nexa.buttons import (
    E_STAR, E_ROCKET, E_GREEN, E_BOLT, E_LOCK, E_STATS, E_ARROW
)
from config import Config

logger = logging.getLogger(__name__)

# ── Wallhaven ─────────────────────────────────────────────────────────
# API key: hardcoded from src-bot (same as reference file)
WALLHAVEN_API_KEY = "FsXt5pwoerVZrsV3DwhRctls8YzUev9H"

# categories=011 → anime+people only (same as src-bot)
# categories=110 → general+anime (old setting — changed to 011)
WALLHAVEN_QUERIES = [
    "anime+girl+portrait", "anime+portrait+face", "anime+girl+close+up",
    "anime+beautiful+face", "anime+school+girl", "anime+school+uniform",
    "anime+sailor+uniform", "anime+fantasy+girl", "anime+magic+girl",
    "anime+witch+girl", "anime+elf+girl", "anime+princess",
    "anime+dark+girl", "anime+gothic+girl", "anime+demon+girl",
    "anime+vampire+girl", "anime+girl+sakura", "anime+girl+nature",
    "anime+girl+sunset", "anime+girl+rain", "anime+girl+snow",
    "anime+girl+flowers", "anime+girl+forest", "anime+girl+summer",
    "anime+girl+winter", "anime+girl+spring", "anime+girl+autumn",
    "anime+kawaii+girl", "anime+cute+girl", "anime+chibi+girl",
    "anime+warrior+girl", "anime+sword+girl", "anime+ninja+girl",
    "anime+knight+girl", "anime+cyberpunk+girl", "anime+girl+ocean",
    "anime+girl+sky", "anime+girl+clouds", "anime+mermaid",
    "anime+girl+night", "anime+girl+stars", "anime+girl+moon",
    "anime+girl+galaxy", "anime+pink+hair+girl", "anime+blue+hair+girl",
    "anime+white+hair+girl", "anime+silver+hair+girl", "anime+red+hair+girl",
    "anime+blonde+anime+girl", "anime+girl+smile", "anime+girl+serious",
    "anime+kimono+girl", "anime+yukata+girl", "anime+shrine+maiden",
    "anime+japanese+girl", "anime+waifu", "anime+girl+4k",
    "anime+girl+aesthetic", "anime+girl+minimal", "anime+cherry+blossom",
    "anime+boy+cool", "anime+couple", "anime+art",
    "beautiful+girl+portrait", "asian+girl+portrait+4k",
    "aesthetic+girl+photography", "beautiful+woman+4k",
    "girl+nature+portrait", "model+photography+portrait",
    "cute+girl+wallpaper", "pretty+girl+face+portrait",
    "girl+sunset+photography", "woman+aesthetic+wallpaper",
    "girl+flowers+photography", "beautiful+eyes+portrait",
    "girl+rain+photography", "woman+forest+portrait",
    "girl+city+night+photography",
]

FALLBACK_IMAGE = "https://l.arzfun.com/duLNg"


async def fetch_random_wallhaven_image() -> str:
    try:
        query = random.choice(WALLHAVEN_QUERIES)
        page  = random.randint(1, 3)
        url   = (
            f"https://wallhaven.cc/api/v1/search"
            f"?categories=011&purity=100&q={query}"
            f"&sorting=random&page={page}&apikey={WALLHAVEN_API_KEY}"
        )
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                data   = await resp.json()
                images = data.get("data", [])
                if not images:
                    # Fallback: no query filter, just random
                    fb = (
                        f"https://wallhaven.cc/api/v1/search"
                        f"?categories=011&purity=100&sorting=random"
                        f"&apikey={WALLHAVEN_API_KEY}"
                    )
                    async with session.get(fb, timeout=timeout) as r2:
                        images = (await r2.json()).get("data", [])
                if not images:
                    return FALLBACK_IMAGE
                chosen  = random.choice(images)
                img_url = chosen.get("path", FALLBACK_IMAGE)
                logger.info(f"Wallhaven | query={query} page={page} | {img_url}")
                return img_url
    except Exception as e:
        logger.error(f"Wallhaven fetch failed: {e}")
        return FALLBACK_IMAGE


# ── /start ────────────────────────────────────────────────────────────

@unzip_client.on_message(filters.private & filters.command("start"))
async def start_bot(client, message: Message):
    from unzipper.database.users import add_user, is_user_in_db as is_user_exist
    try:
        if not await is_user_exist(message.from_user.id):
            await add_user(message.from_user.id)
    except Exception:
        pass

    lang   = await get_language(message.chat.id)
    texts  = STRINGS[lang]
    bot_me = await client.get_me()

    caption = (
        f"<b>{E_STAR} Hello {message.from_user.mention},</b>\n"
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
        await client.send_photo(
            chat_id=message.chat.id,
            photo=photo_url,
            caption=caption,
            reply_markup=Buttons.START,
            reply_parameters=message.id,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        # Photo fail ho toh text fallback
        await message.reply_text(
            caption,
            reply_markup=Buttons.START,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )


# ── Thumbnail commands ────────────────────────────────────────────────

@unzip_client.on_message(filters.private & filters.command(["save", "set_thumb"]))
@unzip_client.handle_erros
async def save_dis_thumb(_, message: Message, texts):
    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    rply    = message.reply_to_message
    if not rply or not rply.photo:
        return await prs_msg.edit(texts["no_replied_msg"])
    await save_thumbnail(message.from_user.id, rply)
    await prs_msg.edit(texts["ok_saving_thumb"])


@unzip_client.on_message(filters.private & filters.command(["thget", "get_thumb"]))
@unzip_client.handle_erros
async def give_my_thumb(_, message: Message, texts):
    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    gthumb  = await get_thumbnail(message.from_user.id, True)
    if not gthumb:
        return await prs_msg.edit(texts["no_thumb"])
    await prs_msg.delete()
    await message.reply_photo(gthumb)
    if path.exists(gthumb):
        remove(gthumb)


@unzip_client.on_message(filters.private & filters.command(["thdel", "del_thumb"]))
@unzip_client.handle_erros
async def delete_my_thumb(_, message: Message, texts):
    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    texist  = await get_thumbnail(message.from_user.id)
    if not texist:
        return await prs_msg.edit(texts["no_thumb"])
    await del_thumbnail(message.from_user.id)
    if path.exists(texist):
        remove(texist)
    await prs_msg.edit(texts["ok_deleting_thumb"])


@unzip_client.on_message(filters.private & filters.command("backup"))
@unzip_client.handle_erros
async def do_backup_files(_, message: Message, texts):
    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    await prs_msg.edit(texts["select_provider"], reply_markup=Buttons.BACKUP)


@unzip_client.on_message(filters.private & filters.command("clean"))
@unzip_client.handle_erros
async def clean_ma_files(_, message: Message, texts):
    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    await prs_msg.edit(texts["ask_clean"], reply_markup=Buttons.CLEAN)


# ── /status ───────────────────────────────────────────────────────────

@unzip_client.on_message(filters.private & filters.command("status"))
@unzip_client.handle_erros
async def show_status(_, message: Message, texts):
    from datetime import datetime, timezone
    from unzipper.database.users import is_user_in_db as is_user_exist

    user_id = message.from_user.id
    in_db = await is_user_exist(user_id)

    now = datetime.now(timezone.utc)
    week_num = now.strftime("%Y-W%W")

    await message.reply(
        f"<b>📋 Account Status</b>\n\n"
        f"<b>👤 User Info:</b>\n"
        f" ↳ <b>ID:</b> <code>{user_id}</code>\n"
        f" ↳ <b>Role:</b> 🆓 Free User\n"
        f" ↳ <b>Status:</b> {'✅ Active' if in_db else '❌ Not Registered'}\n\n"
        f"<b>📊 Monthly Quota:</b>\n"
        f" ↳ <b>Remaining:</b> 10.0 GiB extractions\n\n"
        f"<b>🛡 Warnings:</b>\n"
        f" ↳ ✅ No warnings (0/3)\n\n"
        f"<b>📅 Current Month:</b> {week_num}",
        parse_mode=ParseMode.HTML,
        reply_parameters=message.id
    )


# ── /cancel ───────────────────────────────────────────────────────────

@unzip_client.on_message(filters.private & filters.command("cancel"))
@unzip_client.handle_erros
async def cancel_process(_, message: Message, texts):
    from shutil import rmtree
    from unzipper.database.split_arc import del_split_arc_user
    user_id = message.from_user.id
    await del_split_arc_user(user_id)
    try:
        rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}", ignore_errors=True)
    except Exception:
        pass
    await message.reply(
        texts["canceled"].format("Process cancelled by user"),
        reply_parameters=message.id
    )


# ── /done ─────────────────────────────────────────────────────────────

@unzip_client.on_message(filters.private & filters.command("done"))
@unzip_client.handle_erros
async def finish_split_arc(_, message: Message, texts):
    from unzipper.database.split_arc import get_split_arc_user, del_split_arc_user
    from unzipper.lib.extractor import Extractor, ExtractionFailed
    from unzipper.helpers_nexa.utils import get_files
    from unzipper.helpers_nexa.buttons import E_BATCH, E_CROSS, ICON_ARCHIVE, ICON_CANCEL
    from pyrogram.errors import ReplyMarkupTooLong
    from shutil import rmtree
    from time import time

    user_id = message.from_user.id
    arc_data = await get_split_arc_user(user_id)
    if not arc_data:
        return await message.reply(texts["no_splitted_arc"], reply_parameters=message.id)

    arc_name  = arc_data.get("arc_name")
    password  = arc_data.get("password", "")
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    ext_files_dir = f"{download_path}/extracted"

    prs_msg = await message.reply(texts["processing"], reply_parameters=message.id)
    try:
        exter = Extractor()
        ext_s = time()
        if password:
            await exter.extract(arc_name, ext_files_dir, password)
        else:
            await exter.extract(arc_name, ext_files_dir)
        ext_e = time()

        from unzipper.helpers_nexa.utils import TimeFormatter
        await prs_msg.edit(texts["ok_extract"].format(TimeFormatter(round(ext_e - ext_s) * 1000)))

        files = await get_files(ext_files_dir)
        i_e_buttons = await Buttons.make_files_keyboard(files, user_id, message.chat.id)
        await del_split_arc_user(user_id)
        try:
            await prs_msg.edit(texts["select_files"], reply_markup=i_e_buttons)
        except ReplyMarkupTooLong:
            i_e_buttons = await Buttons.make_files_keyboard(files, user_id, message.chat.id, False)
            await prs_msg.edit(texts["select_files"], reply_markup=i_e_buttons)
    except ExtractionFailed:
        await prs_msg.edit(texts["failed_extract"])
    except Exception as e:
        await prs_msg.edit(texts["failed_main"].format(e))
        rmtree(download_path, ignore_errors=True)
