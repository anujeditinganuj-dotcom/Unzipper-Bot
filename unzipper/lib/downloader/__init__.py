# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from time import time
from re import match, sub
from config import Config
from aiohttp import ClientSession
from pyrogram.types import Message
from aiofiles import open as openfile
from unzipper.helpers_nexa.utils import progress_for_pyrogram, humanbytes
from .errors import InvalidContentType, FileTooLarge, InvalidUrl, HttpStatusError

# HTTP/HTTPS URL regex — exported so other modules can import it
dl_regex = (
    r"((http|https)://)(www.)?"
    r"[a-zA-Z0-9@:%._\+~#?&//=]"
    r"{2,256}\.[a-z]"
    r"{2,6}\b([-a-zA-Z0-9@:%._\+~#?&//=]*)"
)


class Downloader:
    """Download files from direct links or Google Drive share links."""

    def __init__(self) -> None:
        self.gdrive_regex = r"https://drive\.google\.com/file/d/(.*?)/.*?\?usp=sharing"
        self.dl_regex = dl_regex

    async def download(self, url: str, path: str, message: Message = None,
                       redirect: bool = False, cont_type: str = "application/",
                       udt: str = "**Trying to Download!** \n"):
        if match(self.gdrive_regex, url):
            gurl = self._parse_gdrive(url)
            return await self._from_direct_link(
                url=gurl, path=path, message=message,
                redirect=True, cont_type=cont_type, udt=udt
            )
        elif match(self.dl_regex, url):
            return await self._from_direct_link(
                url=url, path=path, message=message,
                redirect=redirect, cont_type=cont_type, udt=udt
            )
        else:
            raise InvalidUrl

    def _parse_gdrive(self, url: str) -> str:
        return sub(
            r"https://drive\.google\.com/file/d/(.*?)/.*?\?usp=sharing",
            r"https://drive.google.com/uc?export=download&id=\1",
            url
        )

    async def _from_direct_link(self, url: str, path: str, message: Message = None,
                                 redirect: bool = False, cont_type: str = "application/",
                                 udt: str = "**Trying to Download!** \n"):
        async with ClientSession() as session:
            async with session.get(url, timeout=None, allow_redirects=redirect) as resp:
                if resp.status == 200:
                    pass
                elif resp.status in (301, 302):
                    # Follow redirect
                    async with session.get(url, timeout=None, allow_redirects=True) as resp2:
                        resp = resp2
                else:
                    raise HttpStatusError

                # FIX: cont_type check only if content_type is set
                if resp.content_type and cont_type not in resp.content_type:
                    raise InvalidContentType

                total = resp.content_length
                # FIX: total can be None — only check if it's set
                if total and int(total) > Config.MAX_DOWNLOAD_SIZE:
                    raise FileTooLarge

                curr = 0
                st   = time()
                async with openfile(path, mode="wb") as f:
                    async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                        if curr > Config.MAX_DOWNLOAD_SIZE:
                            raise FileTooLarge
                        await f.write(chunk)
                        curr += len(chunk)
                        if message:
                            await progress_for_pyrogram(curr, total, udt, message, st)
