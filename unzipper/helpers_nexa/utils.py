# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

# Credits: SpEcHiDe's AnyDL-Bot for progress_for_pyrogram, humanbytes and TimeFormatter

from re import sub
from time import time
from math import floor
from json import loads
from os import path, walk
from functools import partial
from subprocess import Popen, PIPE
from asyncio import get_running_loop


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now  = time()
    diff = now - start
    if diff == 0:
        diff = 0.001  # FIX: Prevent ZeroDivisionError at the very start
    speed = current / diff

    if total:
        if round(diff % 10.00) == 0 or current == total:
            percentage = current * 100 / total
            elapsed_time = round(diff) * 1000
            estimated_total_time = elapsed_time + round((total - current) / speed) * 1000

            elapsed_time         = TimeFormatter(elapsed_time)
            estimated_total_time = TimeFormatter(estimated_total_time)

            progress = "[{0}{1}] \n**📊 Progress**: {2}%\n".format(
                ''.join(["◉" for _ in range(floor(percentage / 5))]),
                ''.join(["◎" for _ in range(20 - floor(percentage / 5))]),
                round(percentage, 2))

            tmp = progress + "{0} of {1}\n**🏃 Speed:** {2}/s\n**⏰ ETA:** {3}\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                estimated_total_time if estimated_total_time != '' else "0 s"
            )
            try:
                await message.edit("{}\n {} \n\n**Powered by @anujedits76**".format(ud_type, tmp))
            except Exception:
                pass
    else:
        tmp = "**📊 Progress:** {0} of {1}\n**🏃 Speed:** {2}/s\n**⏰ ETA:** {3}\n".format(
            humanbytes(current),
            "?",
            humanbytes(speed),
            "unknown"
        )
        try:
            await message.edit("{}\n {} \n\n**Powered by @anujedits76**".format(ud_type, tmp))
        except Exception:
            pass


def humanbytes(size):
    if not size:
        return "N/A"
    try:
        size = int(size)
    except (ValueError, TypeError):
        return "N/A"
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds      = divmod(seconds, 60)
    hours,   minutes      = divmod(minutes, 60)
    days,    hours        = divmod(hours, 24)
    tmp = (
        ((str(days)         + "d, ")  if days         else "") +
        ((str(hours)        + "h, ")  if hours        else "") +
        ((str(minutes)      + "m, ")  if minutes      else "") +
        ((str(seconds)      + "s, ")  if seconds      else "") +
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2] if tmp[:-2] else "0ms"


def run_shell_cmds(command: str) -> str:
    """Execute shell command synchronously and return stdout as string."""
    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    proc.wait()
    out = proc.stdout.read()
    return out[:-1].decode("utf-8") if out else ""


async def run_cmds_on_cr(func, *args, **kwargs):
    """Run a blocking function in a thread-pool executor (non-blocking)."""
    loop = get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))


async def run_shell_cmds_async(command: str) -> str:
    """Async wrapper around run_shell_cmds — use this with await."""
    return await run_cmds_on_cr(run_shell_cmds, command)


async def get_files(fpath: str, filter_fn=None):
    """Returns sorted list of all files inside a folder recursively."""
    path_list = [
        path.join(root, fname)
        for root, _, files in walk(fpath)
        for fname in files
    ]
    if filter_fn:
        path_list = list(filter(filter_fn, path_list))
    return sorted(path_list)


def read_json_sync(name: str, as_items: bool = False):
    """Read a JSON file and return a dict or its items."""
    with open(name, encoding="utf-8") as fs:
        data = loads(fs.read())
        return data.items() if as_items else data


async def rm_mark_chars(text: str) -> str:
    """Remove basic Markdown characters from a string."""
    return sub(r"[*`_]", "", text)
