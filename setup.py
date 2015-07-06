from distutils.core import setup, Extension

version = '221'
defines = [('PACKAGE_VERSION', '"{}"'.format(version))]

_journal = Extension('systemd/_journal',
                     define_macros = defines,
                     libraries = ['systemd'],
                     sources = ['systemd/_journal.c',
                                'systemd/pyutil.c'])
_reader = Extension('systemd/_reader',
                     define_macros = defines,
                     libraries = ['systemd'],
                     sources = ['systemd/_reader.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'])
_daemon = Extension('systemd/_daemon',
                     define_macros = defines,
                     libraries = ['systemd'],
                     sources = ['systemd/_daemon.c',
                                'systemd/pyutil.c'])
id128 = Extension('systemd/id128',
                     define_macros = defines,
                     libraries = ['systemd'],
                     sources = ['systemd/id128.c',
                                'systemd/pyutil.c'])
login = Extension('systemd/login',
                     define_macros = defines,
                     libraries = ['systemd'],
                     sources = ['systemd/login.c',
                                'systemd/pyutil.c',
                                'systemd/strv.c'])
setup (name = 'python-systemd',
       version = version,
       description = 'Native interface to the facilities of systemd',
       author_email = 'david@davidstrauss.net',
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
