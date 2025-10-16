# SPDX-License-Identifier: LGPL-2.1-or-later

project(
        'python-systemd',
        'c',
        version: '236',
        license: 'LGPL-2.1-or-later',
        default_options: ['warning_level=2', 'c_std=c99'],
        meson_version: '>= 1.8.0',
)

# Dependencies
python = import('python').find_installation('python3', pure: false)
python_dep = python.dependency()

fs = import('fs')

libsystemd_dep = dependency('libsystemd')

add_project_arguments(
        '-D_GNU_SOURCE=1',
        '-DPACKAGE_VERSION="@0@"'.format(meson.project_version()),
        '-DLIBSYSTEMD_VERSION=@0@'.format(libsystemd_dep.version()),
        language : 'c',
)

update_constants_py = files('update-constants.py')

subdir('src/systemd')

test(
        'unit',
        find_program(python.full_path()),
        args: [
                '-m', 'pytest',
                '-v',
                python_test_dir,
              ],
        env: { 'PYTHONPATH': meson.current_build_dir() / 'src' },
)

alias_target('update-constants', update_constants)
