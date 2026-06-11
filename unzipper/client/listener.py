# ===================================================================== #
#  Custom async listener — replaces pyromod.listen                      #
#  Python 3.12 compatible: NO loop.run_until_complete() anywhere        #
# ===================================================================== #

import asyncio
import logging
from typing import Dict, Optional

# Global pending listeners: {chat_id: asyncio.Future}
_LISTENERS: Dict[int, asyncio.Future] = {}


def register_listener(chat_id: int) -> asyncio.Future:
    """Create and store a Future for this chat_id."""
    loop = asyncio.get_event_loop()
    fut = loop.create_future()
    _LISTENERS[chat_id] = fut
    return fut


def resolve_listener(chat_id: int, message) -> bool:
    """Called when a message arrives — resolves the Future if one exists."""
    fut = _LISTENERS.pop(chat_id, None)
    if fut and not fut.done():
        fut.set_result(message)
        return True
    return False


def cancel_listener(chat_id: int):
    """Cancel a pending listener (e.g. on timeout)."""
    fut = _LISTENERS.pop(chat_id, None)
    if fut and not fut.done():
        fut.cancel()


async def wait_for_message(chat_id: int, timeout: int = 60):
    """
    Wait for the next message in chat_id.
    Returns the Message or raises asyncio.TimeoutError.
    """
    fut = register_listener(chat_id)
    try:
        return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
    except asyncio.TimeoutError:
        cancel_listener(chat_id)
        raise
