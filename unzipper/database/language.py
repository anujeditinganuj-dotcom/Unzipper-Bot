# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from . import unzipper_db
from unzipper.client.caching import USER_LANG

lang_db = unzipper_db["languages_db"]


async def set_language(user_id: int, lang: str):
    exists = await lang_db.find_one({"_id": user_id})
    if exists:
        await lang_db.update_one({"_id": user_id}, {"$set": {"lang": lang}})
    else:
        await lang_db.insert_one({"_id": user_id, "lang": lang})


async def get_language(user_id: int) -> str:
    # Check in-memory cache first
    if user_id in USER_LANG:
        return USER_LANG[user_id]
    # Fall back to DB
    exists = await lang_db.find_one({"_id": user_id})
    if exists:
        USER_LANG[user_id] = exists["lang"]  # warm the cache
        return exists["lang"]
    return "en"


def get_user_languages():
    """Returns a Motor async cursor (do NOT await — use async for directly)."""
    return lang_db.find({})
