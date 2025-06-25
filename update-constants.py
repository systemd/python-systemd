#/usr/bin/env python3

"""
Read definitions from /usr/include/systemd/sd-messages.h and systemd/id128-defines.h files, convert to ones in systemd/id128-constants.h
"""

import re
import sys
import itertools
import argparse
from pathlib import Path
from collections.abc import Iterable
from typing import cast


REGEX_DEFINE = re.compile(r'^#define\s+(?P<name>SD_MESSAGE_[A-Z0-9_]+)\s+\w+')


parser = argparse.ArgumentParser(description="Convert systemd header definitions to id128 constants.")
parser.add_argument('-i', '--include-dir', type=Path, required=True, help='Path to libsystemd include directory')
parser.add_argument('-s', '--source-dir', type=Path, required=True, help='Path to C source directory')
args = parser.parse_args()


def extract_define_lines(file_path: Path) -> list[str]:
    lines = iter(file_path.open().readlines())
    out: list[str] = []
    for line in lines:
        if line.startswith('#define SD_MESSAGE') and '_STR ' not in line:
            if line.endswith('\\'):
                line = line[:-1] + next(lines)
            out.append(' '.join(line.split()))
    return out


def extract_symbol(line: str) -> str:
    """
    Extract the symbol name from a line defining a constant.

    For example, given the line:
    #define SD_MESSAGE_USER_STARTUP_FINISHED SD_ID128_MAKE(ee,d0,0a,68,ff,d8,4e,31,88,21,05,fd,97,3a,bd,d1)
    this function will return:
    SD_MESSAGE_USER_STARTUP_FINISHED
    or empty string if the line does not match the expected format.
    """
    if match := REGEX_DEFINE.match(line):
        return match.group('name')
    return ''


def build_line_for_constant(name: str) -> str:
    return f'add_id(m, "{name}", {name}) JOINER'


def update_docs(source_dir: Path, symbols: Iterable[str]):
    doc_file = source_dir.joinpath('../docs/id128.rst')
    headers = doc_file.read_text().splitlines()[:9]
    lines = [f'   .. autoattribute:: systemd.id128.{s}' for s in symbols]
    new_content = '\n'.join(headers + lines) + '\n'
    doc_file.write_text(new_content)
    rel_doc_path = doc_file.resolve().relative_to(Path('.').resolve(), walk_up=True)
    print(f'Updated {rel_doc_path}.', file=sys.stderr)


def main():
    source_files = [cast(Path, args.include_dir).joinpath('systemd/sd-messages.h'), cast(Path, args.source_dir).joinpath('id128-defines.h')]
    print(f'To extract symbols from {source_files}...', file=sys.stderr)
    source_lines = tuple(itertools.chain.from_iterable(extract_define_lines(file) for file in source_files))
    print(f'Read {len(source_lines)} lines.', file=sys.stderr)
    symbols = tuple(sorted(frozenset(s for line in source_lines if (s := extract_symbol(line)))))
    print(f'Found {len(symbols)} unique symbols.', file=sys.stderr)
    converted_lines = tuple(build_line_for_constant(s) for s in symbols)
    print(f'Converted to {len(converted_lines)} lines.', file=sys.stderr)
    dest_file = cast(Path, args.source_dir).joinpath('id128-constants.h')
    dest_file.write_text('\n'.join(converted_lines) + '\n')
    print(f'Wrote {len(converted_lines)} constants to {dest_file}.', file=sys.stderr)
    update_docs(cast(Path, args.source_dir), symbols)
    print('🎉 Done.', file=sys.stderr)


if __name__ == '__main__':
    main()
