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

# Docs
sphinx_build = find_program('sphinx-build', disabler: true, required: get_option('docs'))
sphinx_args = ['-Dversion=' + meson.project_version(), '-Drelease=' + meson.project_version()]

input_dir = meson.current_source_dir() / 'docs'
output_dir = meson.current_build_dir() / 'html'
doc_target = custom_target('html',
        output: 'html',
        input: files('docs/conf.py',
                     'docs/daemon.rst', 'docs/id128.rst',
                     'docs/journal.rst', 'docs/login.rst',
                     'docs/layout.html', 'docs/default.css'),
        command: [sphinx_build, '-b', 'html', sphinx_args, input_dir, output_dir],
        env: { 'PYTHONPATH': meson.current_build_dir() / 'src' },
        build_by_default: get_option('docs'),
        install: get_option('docs'),
        install_dir: get_option('datadir') / 'doc' / meson.project_name()
)
