from distutils.core import setup, Extension

cjournald = Extension('journald/_journald',
                      libraries = ['systemd-journal'],
                      sources = ['journald/_journald.c'])

setup (name = 'journald',
       version = '0.1',
       description = 'Native interface to the journald facilities of systemd',
       author_email = 'david@davidstrauss.net',
       url = 'https://github.com/davidstrauss/journald-python',
       py_modules = ['journald'],
       ext_modules = [cjournald])
