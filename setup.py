from distutils.core import setup, Extension

cjournal = Extension('systemd/_journal',
                      libraries = ['systemd-journal'],
                      sources = ['systemd/_journal.c'])

setup (name = 'systemd',
       version = '0.1',
       description = 'Native interface to the facilities of systemd',
       author_email = 'david@davidstrauss.net',
       url = 'https://github.com/systemd/python-systemd',
       py_modules = ['systemd.journal'],
       ext_modules = [cjournal])
