import sys, os
from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
from subprocess import Popen, PIPE, check_output


class build_ext_generate_id128_header(build_ext):
    def run(self):
        if not self.dry_run and not os.path.exists("systemd/id128-constants.h"):
            sysroot = os.environ.get('SYSROOT', '/')
            sd_messages_h = os.path.join(sysroot, "usr/include/systemd/sd-messages.h")
            constants = [line.split()[1]
                         for line in open(sd_messages_h)
                         if line.startswith('#define SD_MESSAGE_')]

            with open("systemd/id128-constants.h", "w") as f:
                for c in constants:
                    f.write('add_id(m, "{0}", {0}) JOINER\n'.format(c))

        return build_ext.run(self)


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
    pkgconf = os.getenv('PKG_CONFIG', 'pkg-config')
    status, result = call(pkgconf, '--libs', '--cflags', package)
    if status != 0:
        return status, result
    for token in result.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    version = check_output([pkgconf, '--modversion', package],
                           universal_newlines=True).strip()
    pair = (package.replace('-', '_').upper() + '_VERSION', version)
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

version = '231'
defines = {'define_macros':[('PACKAGE_VERSION', '"{}"'.format(version))]}

_journal = Extension('systemd/_journal',
                     sources = ['systemd/_journal.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-journal', **defines))
_reader = Extension('systemd/_reader',
                     sources = ['systemd/_reader.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     **lib('libsystemd', 'libsystemd-journal', **defines))
_daemon = Extension('systemd/_daemon',
                     sources = ['systemd/_daemon.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-daemon', **defines))
id128 = Extension('systemd/id128',
                     sources = ['systemd/id128.c',
                                'systemd/pyutil.c'],
                     **lib('libsystemd', 'libsystemd-id128', **defines))
login = Extension('systemd/login',
                     sources = ['systemd/login.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'],
                     **lib('libsystemd', 'libsystemd-login', **defines))
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
       py_modules = ['systemd.journal', 'systemd.daemon',
                     'systemd.test.test_daemon', 'systemd.test.test_journal'],
       ext_modules = [_journal,
                      _reader,
                      _daemon,
                      id128,
                      login],
       cmdclass = {'build_ext': build_ext_generate_id128_header})
