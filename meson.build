project(
        'python-systemd',
        'c',
        version: '236',
        license: 'LGPL-2.1-or-later',
        default_options: ['warning_level=2', 'c_std=c99'],
)

# Dependencies
python = import('python').find_installation('python3', pure: false)
python_dep = python.dependency()

# Try to find libsystemd
foreach name : [
        'libsystemd',
        'libsystemd-journal',
        'libsystemd-daemon',
        'libsystemd-id128',
        'libsystemd-login',
]
        libsystemd_dep = dependency(name, required: false)
        if libsystemd_dep.found()
                break
        endif
endforeach

# Common compile arguments matching setup.py
common_c_args = [
        '-std=c99',
        '-Werror=implicit-function-declaration',
        '-DPACKAGE_VERSION="' + meson.project_version() + '"',
        '-DLIBSYSTEMD_VERSION=' + libsystemd_dep.version(),
]

# Build _journal extension module
python.extension_module(
        '_journal',
        ['systemd/_journal.c', 'systemd/pyutil.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build _reader extension module
python.extension_module(
        '_reader',
        ['systemd/_reader.c', 'systemd/pyutil.c', 'systemd/strv.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build _daemon extension module
python.extension_module(
        '_daemon',
        ['systemd/_daemon.c', 'systemd/pyutil.c', 'systemd/util.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build id128 extension module
python.extension_module(
        'id128',
        ['systemd/id128.c', 'systemd/pyutil.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Build login extension module
python.extension_module(
        'login',
        ['systemd/login.c', 'systemd/pyutil.c', 'systemd/strv.c'],
        dependencies: [libsystemd_dep],
        c_args: common_c_args,
        install: true,
        subdir: 'systemd',
)

# Install Python modules (matching py_modules in setup.py)
python.install_sources(
        'systemd/__init__.py',
        'systemd/journal.py',
        'systemd/daemon.py',
        subdir: 'systemd',
)

# Install test modules
python.install_sources(
        'systemd/test/test_daemon.py',
        'systemd/test/test_journal.py',
        'systemd/test/test_login.py',
        'systemd/test/test_id128.py',
        subdir: 'systemd/test',
)
