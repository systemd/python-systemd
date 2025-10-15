# SPDX-License-Identifier: LGPL-2.1-or-later

# Build _journal extension module
python.extension_module(
        '_journal',
        ['_journal.c', 'pyutil.c'],
        dependencies: [libsystemd_dep],
        install: true,
        subdir: 'systemd',
)

# Build _reader extension module
python.extension_module(
        '_reader',
        ['_reader.c', 'pyutil.c', 'strv.c'],
        dependencies: [libsystemd_dep],
        install: true,
        subdir: 'systemd',
)

# Build _daemon extension module
python.extension_module(
        '_daemon',
        ['_daemon.c', 'pyutil.c', 'util.c'],
        dependencies: [libsystemd_dep],
        install: true,
        subdir: 'systemd',
)

# Build id128 extension module
python.extension_module(
        'id128',
        ['id128.c', 'pyutil.c'],
        dependencies: [libsystemd_dep],
        install: true,
        subdir: 'systemd',
)

# Build login extension module
python.extension_module(
        'login',
        ['login.c', 'pyutil.c', 'strv.c'],
        dependencies: [libsystemd_dep],
        install: true,
        subdir: 'systemd',
)

# Install Python modules
python.install_sources(
        '__init__.py',
        'journal.py',
        'daemon.py',
        subdir: 'systemd',
)

# Install test modules
python.install_sources(
        'test/test_daemon.py',
        'test/test_journal.py',
        'test/test_login.py',
        'test/test_id128.py',
        subdir: 'systemd/test',
)

include_dir = libsystemd_dep.get_variable(pkgconfig: 'includedir')

update_constants = custom_target(
        output: 'update-constants-impl',
        command: [
                update_constants_py,
                meson.current_source_dir() / 'id128-constants.h',
                meson.project_source_root() / 'docs/id128.rst',
                meson.current_source_dir() / 'id128-defines.h',
                include_dir / 'systemd/sd-messages.h',
        ])
