import sys, os
from setuptools import setup, Extension
from subprocess import Popen, PIPE, check_output

def call(*cmd):
    cmd = Popen(cmd,
                stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
    if cmd.wait() == 0:
        return cmd.returncode, cmd.stdout.read()
    else:
        return cmd.returncode, cmd.stderr.read()

def pkgconfig(package, **kw):
    pkg_version = package.replace('-', '_').upper() + '_VERSION'
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    pkgconf = os.getenv('PKG_CONFIG', 'pkg-config')
    status, result = call(pkgconf, '--libs', '--cflags', package)
    if status != 0:
        return status, result
    for token in result.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

    # allow version detection to be overridden using environment variables
    version = os.getenv(pkg_version)
    if not version:
        version = check_output([pkgconf, '--modversion', package],
                               universal_newlines=True).strip()
    pair = (pkg_version, version)
    defines = kw.setdefault('define_macros', [])
    if pair not in defines:
        defines.append(pair)
    return status, kw

def lib(*names, **kw):
    if '--version' in sys.argv:
        return {}
    results = []
    for name in names:
        status, result = pkgconfig(name, **kw)
        if status == 0:
            return result
        results.append(result)
    sys.stderr.write('Cannot find ' + ' or '.join(names) + ':\n\n'
                     + '\n'.join(results) + '\n')
    sys.exit(status)

version = '235'
defines = {'define_macros':[('PACKAGE_VERSION', '"{}"'.format(version))]}

_journal = Extension('systemd/_journal',
                     sources = ['systemd/_journal.c',
                                'systemd/pyutil.c'],
                     extra_compile_args=['-std=c99', '-Werror=implicit-function-declaration'],
                     **lib('libsystemd', 'libsystemd-journal', **defines))
_reader = Extension('systemd/_reader',
                     sources = ['systemd/_reader.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     extra_compile_args=['-std=c99', '-Werror=implicit-function-declaration'],
                     **lib('libsystemd', 'libsystemd-journal', **defines))
_daemon = Extension('systemd/_daemon',
                     sources = ['systemd/_daemon.c',
                                'systemd/pyutil.c',
                                'systemd/util.c'],
                     extra_compile_args=['-std=c99', '-Werror=implicit-function-declaration'],
                     **lib('libsystemd', 'libsystemd-daemon', **defines))
id128 = Extension('systemd/id128',
                     sources = ['systemd/id128.c',
                                'systemd/pyutil.c'],
                     extra_compile_args=['-std=c99', '-Werror=implicit-function-declaration'],
                     **lib('libsystemd', 'libsystemd-id128', **defines))
login = Extension('systemd/login',
                     sources = ['systemd/login.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     extra_compile_args=['-std=c99', '-Werror=implicit-function-declaration'],
                     **lib('libsystemd', 'libsystemd-login', **defines))
setup (name = 'systemd-python',
       version = version,
       description = 'Python interface for libsystemd',
       author_email = 'david@davidstrauss.net',
       maintainer = 'systemd developers',
       maintainer_email = 'systemd-devel@lists.freedesktop.org',
       url = 'https://github.com/systemd/python-systemd',
       license = 'LGPLv2+',
       classifiers = [
           'Programming Language :: Python :: 2',
           'Programming Language :: Python :: 3',
           'Topic :: Software Development :: Libraries :: Python Modules',
           'Topic :: System :: Logging',
           'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
           ],
       py_modules = ['systemd.journal', 'systemd.daemon',
                     'systemd.test.test_daemon',
                     'systemd.test.test_journal',
                     'systemd.test.test_login',
                     'systemd.test.test_id128'],
       ext_modules = [_journal,
                      _reader,
                      _daemon,
                      id128,
                      login])
