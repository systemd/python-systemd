#!/usr/bin/env python3

import os
import subprocess

from datetime import datetime
from typing import Optional


def git_describe() -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "describe", "--abbrev=9", "--tags", "--match=*[0-9]*"],
        text=True,
        capture_output=True,
    )


def version_from_git_describe(desc: str, timestamp: Optional[datetime] = None) -> str:
    desc = desc.removeprefix("v").strip()
    version, *rest = desc.split("-", maxsplit=2)
    # we're directly on a tag
    if not rest:
        return version

    # guess next version
    version_parts = [int(v) for v in version.split(".")]
    version_parts.append(version_parts.pop() + 1)

    # dev tailer
    commits_since_tag, commit = rest
    t = timestamp or datetime.now()
    trailer = f".dev{commits_since_tag}+{commit}.d{t:%Y%m%d}"

    return ".".join(str(v) for v in version_parts) + trailer


def read_git_archival_txt() -> dict[str, str]:
    content = open(".git_archival.txt").read()
    return {key.rstrip(":"): val for line in content.splitlines()}


def version_from_archival_txt(info: dict[str, str], timestamp: Optional[datetime] = None) -> str:
    desc = info['describe-name']

    t = timestamp or datetime.fromisoformat(info['node-date'])
    return version_from_git_describe(desc, timestamp=t)


def main() -> str:
    # if SOURCE_DATE_EPOCH is set, we're going to use it as the timestamp
    sde = None
    if (t := os.environ.get("SOURCE_DATE_EPOCH")) is not None:
        sde = datetime.fromtimestamp(int(t))

    p = git_describe()
    if p.returncode == 0:
        return version_from_git_describe(p.stdout, timestamp=sde)
    elif p.returncode == 128:  # not a git repo
        info = read_git_archival_txt()
        return version_from_archival_txt(info, timestamp=sde)

    return "unknown"


if __name__ == "__main__":
    print(main())
