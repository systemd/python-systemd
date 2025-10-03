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

subdir('src')

