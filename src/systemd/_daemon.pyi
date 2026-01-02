import socket
from typing import Final, SupportsIndex

from typing_extensions import Unpack
from _typeshed import StrOrBytesPath, SupportsLenAndGetItem

__version__: Final[str]

LISTEN_FDS_START: Final[int]

def booted() -> bool: ...
def notify(status: str,
           unset_environment: bool = False,
           pid: SupportsIndex = 0,
           fds: SupportsLenAndGetItem[SupportsIndex] = []) -> bool: ...
def _listen_fds(unset_environment: bool = True) -> int: ...
def _listen_fds_with_names(unset_environment: bool = True) -> tuple[int, Unpack[tuple[str, ...]]]: ...
def _is_fifo(fd: SupportsIndex, path: StrOrBytesPath | None = None, /) -> bool: ...
def _is_mq(fd: SupportsIndex, path: StrOrBytesPath | None = None, /) -> bool: ...
def _is_socket(fd: SupportsIndex,
               family: SupportsIndex = socket.AF_UNSPEC,
               type: SupportsIndex = 0,
               listening: SupportsIndex = -1,
               /) -> bool: ...
def _is_socket_inet(fd: SupportsIndex,
                    family: SupportsIndex = socket.AF_UNSPEC,
                    type: SupportsIndex = 0,
                    listening: SupportsIndex = -1,
                    port: SupportsIndex = 0,
                    /) -> bool: ...
def _is_socket_sockaddr(fd: SupportsIndex,
                        address: str,
                        type: SupportsIndex = 0,
                        flowinfo: SupportsIndex = 0,
                        listening: SupportsIndex = -1,
                        /) -> bool: ...
def _is_socket_unix(fd: SupportsIndex,
                    type: SupportsIndex = 0,
                    listening: SupportsIndex = -1,
                    path: StrOrBytesPath | None = None,
                    /) -> bool: ...
