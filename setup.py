from distutils.core import setup, Extension

journald = Extension('journald',
                     libraries = ['systemd-journal'],
                     sources = ['journald.c'])

setup (name = 'journald',
       version = '0.1',
       description = 'Native interface to the journald facilities of systemd',
       author_email = 'david@davidstrauss.net',
       url = 'https://github.com/davidstrauss/journald-python',
       ext_modules = [journald])
