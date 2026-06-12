# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
# ===================================================================== #

from os import path, makedirs
from subprocess import Popen, PIPE
from .errors import ExtractionFailed
from unzipper.helpers_nexa.utils import run_cmds_on_cr


def _run_cmd_with_code(command: str):
    """Run shell command and return (stdout, returncode)."""
    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    stdout = (out or b"").decode("utf-8", errors="replace").strip()
    return stdout, proc.returncode


class Extractor:
    """Extract archives using 7z and zstd."""

    def __init__(self) -> None:
        pass

    async def extract(self, arc_path: str, out: str,
                      password: str = "", splitted: bool = False):
        if path.splitext(arc_path)[1] == ".zst":
            makedirs(out, exist_ok=True)
            ex, code = await run_cmds_on_cr(_run_cmd_with_code,
                f'zstd -f --output-dir-flat "{out}" -d "{arc_path}"')
            if code != 0:
                raise ExtractionFailed
            return ex
        else:
            makedirs(out, exist_ok=True)
            if password:
                cmd = f'7z x -o"{out}" -p"{password}" "{arc_path}" -y'
            else:
                cmd = f'7z x -o"{out}" "{arc_path}" -y'
            if splitted:
                cmd += " -tsplit"
            ex, code = await run_cmds_on_cr(_run_cmd_with_code, cmd)
            # 7z exit codes: 0=OK, 1=Warning(still extracted), 2+=Fatal error
            if code not in (0, 1):
                raise ExtractionFailed
            return ex
