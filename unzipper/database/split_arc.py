# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from . import unzipper_db

spl_db = unzipper_db["splitted_archive_users"]


async def add_split_arc_user(uid: int, fn: str, passw: str):
    # FIX: Use upsert instead of raising ValueError if already exists
    await spl_db.update_one(
        {"_id": uid},
        {"$set": {"file_name": fn, "password": passw}},
        upsert=True
    )


async def get_split_arc_user(uid: int):
    doc = await spl_db.find_one({"_id": uid})
    if doc:
        return True, doc["file_name"], doc["password"]
    return False, None, None


async def del_split_arc_user(uid: int):
    await spl_db.delete_one({"_id": uid})
