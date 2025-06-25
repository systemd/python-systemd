# Build _journal extension module
python.extension_module(
        '_journal',
        ['_journal.c', 'pyutil.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build _reader extension module
python.extension_module(
        '_reader',
        ['_reader.c', 'pyutil.c', 'strv.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build _daemon extension module
python.extension_module(
        '_daemon',
        ['_daemon.c', 'pyutil.c', 'util.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build id128 extension module
python.extension_module(
        'id128',
        ['id128.c', 'pyutil.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build login extension module
python.extension_module(
        'login',
        ['login.c', 'pyutil.c', 'strv.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Install Python modules (matching py_modules in setup.py)
python.install_sources('__init__.py', 'journal.py', 'daemon.py', subdir: 'systemd')

# Install test modules
python.install_sources(
        'test/test_daemon.py',
        'test/test_journal.py',
        'test/test_login.py',
        'test/test_id128.py',
        subdir: 'systemd/test',
)
