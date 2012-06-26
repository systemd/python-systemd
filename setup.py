from distutils.core import setup, Extension

journald = Extension('journald',
                    sources = ['journald.c'])

setup (name = 'journald',
       version = '0.1',
       description = 'Native interface to the journald facilities of systemd',
       ext_modules = [journald])
