from typing import Final, SupportsIndex

__version__: Final[str]

def sendv(*args: str | bytes) -> None: ...
def stream_fd(identifier: str,
              priority: SupportsIndex,
              level_prefix: SupportsIndex) -> int: ...
