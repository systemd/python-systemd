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

subdir('src')

test(
        'pytest',
        python,
        args: [
                '-m', 'pytest',
                meson.project_source_root() / 'src/systemd/test',
        ],
        workdir: meson.project_build_root(),
)

run_target(
        'doc',
        command: [
                python,
                '-m', 'sphinx',
                '-b', 'html',
                '-D', 'version=' + meson.project_version(),
                '-D', 'release=' + meson.project_version(),
                '@SOURCE_ROOT@/docs',
                'html',
        ],
)

run_target(
        'update-constants',
        command: [
                python,
                files('update-constants.py'),
                '-i', libsystemd_dep.get_variable('includedir'),
                '-s', meson.project_source_root() / 'systemd',
        ],
)

# Trick to keep Meson from demanding other tools to be available at building Python extention time.
env_bin = find_program('env', required: false)

# Run target to generate TAGS file for Emacs
run_target(
        'ctags',
        command: [env_bin, 'ctags', '-R', '@SOURCE_ROOT@/src/systemd'],
)


# Sync built HTML docs to the remote server using rsync.
run_target(
        'doc-sync',
        command: [
                env_bin,
                'rsync',
                '-rlv',
                '--delete',
                '--omit-dir-times', 'html/',
                'www.freedesktop.org:/srv/www.freedesktop.org/www/software/systemd/python-systemd/',
        ],
)

# Upload distribution tarball and signature using twine-3.
version = meson.project_version()
archive = 'dist/systemd-python-' + version + '.tar.gz'
signature_filename = 'systemd-python-' + version + '.tar.gz.asc'

# Run target to sign the distribution tarball using GPG.
run_target(
        'sign',
        command: [env_bin, 'gpg', '--detach-sign', '-a', archive],
)

# NOTE: Run 'sign' target before 'upload' to ensure the signature file exists.
run_target(
        'upload',
        command: [python, '-m', 'twine', 'upload', archive, signature_filename],
)
