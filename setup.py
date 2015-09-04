import sys, os
from distutils.core import setup, Extension
from subprocess import Popen, PIPE

def call(*cmd):
    cmd = Popen(cmd,
                stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
    if cmd.wait() == 0:
        return cmd.returncode, cmd.stdout.read()
    else:
        return cmd.returncode, cmd.stderr.read()

def pkgconfig(package, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    status, result = call('pkg-config', '--libs', '--cflags', package)
    if status != 0:
        return status, result
    for token in result.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return status, kw

def lib(*names):
    if '--version' in sys.argv:
        return {}
    results = []
    for name in names:
        status, result = pkgconfig(name)
        if status == 0:
            return result
        results.append(result)
    sys.stderr.write('Cannot find ' + ' or '.join(names) + ':\n\n'
                     + '\n'.join(results) + '\n')
    sys.exit(status)

version = '230'
defines = [('PACKAGE_VERSION', '"{}"'.format(version))]

_journal = Extension('systemd/_journal',
                     define_macros = defines,
                     sources = ['systemd/_journal.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-journal'))
_reader = Extension('systemd/_reader',
                     define_macros = defines,
                     sources = ['systemd/_reader.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     **lib('libsystemd', 'libsystemd-journal'))
_daemon = Extension('systemd/_daemon',
                     define_macros = defines,
                     sources = ['systemd/_daemon.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-daemon'))
id128 = Extension('systemd/id128',
                     define_macros = defines,
                     sources = ['systemd/id128.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-id128'))
login = Extension('systemd/login',
                     define_macros = defines,
                     sources = ['systemd/login.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     **lib('libsystemd', 'libsystemd-login'))
setup (name = 'python-systemd',
       version = version,
       description = 'Native interface to the facilities of systemd',
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
       py_modules = ['systemd.journal', 'systemd.daemon'],
       ext_modules = [_journal,
                      _reader,
                      _daemon,
                      id128,
                      login])
