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

libsystemd_dep = dependency('libsystemd')

common_c_args = [
        '-DPACKAGE_VERSION="@0@"'.format(meson.project_version()),
        '-DLIBSYSTEMD_VERSION=@0@'.format(libsystemd_dep.version()),
]

subdir('src/systemd')

# Docs
sphinx_build = find_program('sphinx-build', disabler: true, required: get_option('docs'))
if get_option('docs')
        sphinx_args = ['-Dversion=' + meson.project_version(), '-Drelease=' + meson.project_version()]
        input_dir = meson.current_source_dir() / 'docs'
        output_dir = meson.current_build_dir() / 'html'
        output_file = output_dir / 'index.html'
        custom_target('build-docs',
                output: 'index.html',
                input: files('docs/conf.py'),
                command: [sphinx_build, '-b', 'html', sphinx_args, input_dir, output_dir],
        )
endif
