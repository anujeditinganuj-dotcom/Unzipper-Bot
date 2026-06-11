# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from asyncio import sleep
from shutil import disk_usage as sdisk_usage

from config import Config
from pyrogram import filters
from unzipper import unzip_client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from unzipper.helpers_nexa.utils import humanbytes

from unzipper.database.users import (
    add_banned_user, count_banned_users,
    count_users, del_banned_user, del_user,
    get_users_list
)
from psutil import cpu_percent, disk_usage, net_io_counters, virtual_memory


@unzip_client.on_message(filters.private & filters.command("stats"))
@unzip_client.handle_erros
async def send_stats(_, message: Message, texts):
    stats_msg = await message.reply(texts["processing"])

    frmow = message.from_user and message.from_user.id == Config.BOT_OWNER

    total, used, free = sdisk_usage(".")
    cpu_usage  = cpu_percent()
    ram_usage  = virtual_memory().percent
    cdisk_pct  = disk_usage("/").percent
    net_usage  = net_io_counters()
    total_u    = await count_users()
    total_ban  = await count_banned_users()

    usrtxt = (
        f"\n**👥 Users:**\n"
        f" ↳**Users in Database:** `{total_u}`\n"
        f" ↳**Total Banned Users:** `{total_ban}`\n\n"
    ) if frmow else ""

    await stats_msg.edit(
        f"**💫 Current Bot Stats 💫**\n"
        f"{usrtxt}"
        f"**🌐 Bandwidth Usage,**\n"
        f" ↳ **Sent:** `{humanbytes(net_usage.bytes_sent)}`\n"
        f" ↳ **Received:** `{humanbytes(net_usage.bytes_recv)}`\n\n"
        f"**💾 Disk Usage,**\n"
        f" ↳**Total:** `{humanbytes(total)}`\n"
        f" ↳**Used:** `{humanbytes(used)} ({cdisk_pct}%)`\n"
        f" ↳**Free:** `{humanbytes(free)}`\n\n"
        f"**🎛 Hardware Usage,**\n"
        f" ↳**CPU:** `{cpu_usage}%`\n"
        f" ↳**RAM:** `{ram_usage}%`"
    )


async def _do_broadcast(message, user):
    try:
        await message.copy(chat_id=int(user))
        return 200
    except FloodWait as e:
        # FIX: .value for new pyrogram, .x for legacy
        wait = e.value if hasattr(e, "value") else e.x
        await sleep(wait)
        return await _do_broadcast(message, user)  # FIX: was missing await
    except Exception:
        await del_user(int(user))
        return 0


@unzip_client.on_message(
    filters.private & filters.command("broadcast") & filters.user(Config.BOT_OWNER)
)
@unzip_client.handle_erros
async def broadcast_dis(_, message: Message, texts):
    bc_msg = await message.reply(texts["processing"])
    r_msg  = message.reply_to_message
    if not r_msg:
        return await bc_msg.edit(texts["no_replied_msg"])

    await bc_msg.edit(texts["broadcast_started"])
    success_no = 0
    failed_no  = 0
    total_users = await count_users()

    # FIX: async for on async generator — no await
    async for user in get_users_list():
        result = await _do_broadcast(r_msg, user)
        if result == 200:
            success_no += 1
        else:
            failed_no += 1

    await bc_msg.edit(texts["boradcast_results"].format(total_users, success_no, failed_no))


@unzip_client.on_message(
    filters.private & filters.command("ban") & filters.user(Config.BOT_OWNER)
)
@unzip_client.handle_erros
async def ban_user(_, message: Message, texts):
    ban_msg = await message.reply(texts["processing"])
    try:
        user_id = message.text.split(None, 1)[1]
    except IndexError:
        return await ban_msg.edit(texts["no_userid"])
    if not user_id.isnumeric():
        return await ban_msg.edit(texts["no_userid"])
    await add_banned_user(int(user_id))
    await ban_msg.edit(texts["ok_ban"].format(user_id))


@unzip_client.on_message(
    filters.private & filters.command("unban") & filters.user(Config.BOT_OWNER)
)
@unzip_client.handle_erros
async def unban_user(_, message: Message, texts):
    unban_msg = await message.reply(texts["processing"])
    try:
        user_id = message.text.split(None, 1)[1]
    except IndexError:
        return await unban_msg.edit(texts["no_userid"])
    if not user_id.isnumeric():
        return await unban_msg.edit(texts["no_userid"])
    await del_banned_user(int(user_id))
    await unban_msg.edit(texts["ok_unban"].format(user_id))
