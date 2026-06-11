import logging
import asyncio
from json import loads

USER_LANG = {}
STRINGS   = {}


def update_text_strings():
    """Load all localization JSON files into STRINGS (sync, called at import time)."""
    def _read(file, as_items=False):
        with open(file, encoding="utf-8") as f:
            data = loads(f.read())
            return data.items() if as_items else data

    for lcode, _ in _read("unzipper/localization/languages.json", as_items=True):
        STRINGS[lcode] = _read(f"unzipper/localization/{lcode}/messages.json")

    STRINGS["buttons"] = _read("unzipper/localization/defaults/buttons.json")


def update_languages_cache():
    """
    Schedule USER_LANG population from DB.
    Must be called AFTER the event loop and bot are running.
    get_user_languages() returns a Motor cursor — do NOT await it.
    """
    from unzipper.database.language import get_user_languages

    async def _run():
        try:
            # FIX: Motor cursor is NOT awaitable, iterate directly
            async for doc in get_user_languages():
                USER_LANG[doc["_id"]] = doc["lang"]
        except Exception as e:
            logging.warning(f"Language cache update failed: {e}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_run())
        else:
            loop.run_until_complete(_run())
    except Exception as e:
        logging.warning(f"Could not schedule language cache: {e}")


def update_cache():
    """Called at import time — only loads text strings (no DB needed yet)."""
    logging.info(" >> Updating text strings cache...")
    update_text_strings()
