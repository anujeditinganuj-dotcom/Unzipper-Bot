# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from os import path, makedirs
from .errors import ExtractionFailed
from unzipper.helpers_nexa.utils import run_shell_cmds, run_cmds_on_cr


class Extractor:
    """Extract archives using 7z and zstd."""

    def __init__(self) -> None:
        pass

    async def extract(self, arc_path: str, out: str,
                      password: str = "", splitted: bool = False):
        if path.splitext(arc_path)[1] == ".zst":
            makedirs(out, exist_ok=True)   # FIX: exist_ok so no FileExistsError
            ex = await self._ext_zstd(out, arc_path)
            await self.__check_output(ex)
            return ex
        else:
            makedirs(out, exist_ok=True)   # FIX: also create for 7z target
            ex = await self._ext_7z(out, arc_path, password, splitted)
            await self.__check_output(ex)
            return ex

    async def _ext_7z(self, out: str, arc_path: str,
                      password: str = "", splitted: bool = False) -> str:
        if password:
            cmd = f'7z x -o"{out}" -p"{password}" "{arc_path}" -y'
        else:
            cmd = f'7z x -o"{out}" "{arc_path}" -y'
        if splitted:
            cmd += " -tsplit"
        return await run_cmds_on_cr(run_shell_cmds, cmd)

    async def _ext_zstd(self, out: str, arc_path: str) -> str:
        cmd = f'zstd -f --output-dir-flat "{out}" -d "{arc_path}"'
        return await run_cmds_on_cr(run_shell_cmds, cmd)

    async def __check_output(self, out: str):
        if out and any(e in out for e in ["Error", "Can't open as archive"]):
            raise ExtractionFailed
