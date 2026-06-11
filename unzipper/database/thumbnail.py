# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from os import path, makedirs
from PIL import Image
from . import unzipper_db
from requests import post
from pyrogram.types import Message
from unzipper.lib.downloader import Downloader
from unzipper.helpers_nexa.utils import run_cmds_on_cr


thumb_db = unzipper_db["thumbnails_db"]


def upload_thumbnail(img: str):
    try:
        with open(img, "rb") as file:
            rs = post(
                "https://telegra.ph/upload",
                files={"file": file},
                timeout=30
            ).json()[0]
            return f"https://telegra.ph{rs['src']}"
    except Exception as e:
        raise Exception(f"Thumbnail upload failed: {e}")


def prepare_thumb(ipath):
    tpath = f"{path.splitext(ipath)[0]}.thumb.jpg"
    with Image.open(ipath) as im:
        rim = im.convert("RGB")
        rim.thumbnail((320, 320))
        rim.save(tpath, "JPEG")
    return tpath


async def save_thumbnail(uid: int, message: Message):
    # Download the image
    ip = await message.download()
    thumb = await run_cmds_on_cr(prepare_thumb, ip)
    up_thumb = await run_cmds_on_cr(upload_thumbnail, thumb)
    is_exist = await thumb_db.find_one({"_id": uid})
    if is_exist:
        await thumb_db.update_one({"_id": uid}, {"$set": {"url": up_thumb}})
    else:
        await thumb_db.insert_one({"_id": uid, "url": up_thumb})


async def get_thumbnail(user_id: int, download: bool = False):
    gtm = await thumb_db.find_one({"_id": user_id})
    if gtm:
        if download:
            makedirs("Dump", exist_ok=True)
            dimg = f"Dump/thumbnail_{path.basename(gtm['url'])}"
            await Downloader().download(gtm["url"], dimg, cont_type="image/")
            return dimg
        return gtm["url"]
    else:
        return None


async def del_thumbnail(user_id: int):
    is_exist = await thumb_db.find_one({"_id": user_id})
    if is_exist:
        await thumb_db.delete_one({"_id": user_id})
    else:
        return
