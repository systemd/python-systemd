PYTHON = python
SED = sed
SPHINX_BUILD = sphinx-build
ETAGS = etags
INCLUDE_DIR = /usr/include/
VERSION := $(shell $(PYTHON) setup.py --version)
TESTFLAGS = -v

define buildscript
import sys,sysconfig
print("build/lib.{}-{}.{}".format(sysconfig.get_platform(), *sys.version_info[:2]))
endef

builddir := $(shell $(PYTHON) -c '$(buildscript)')

all: build

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install --skip-build $(if $(DESTDIR),--root $(DESTDIR))

dist:
	$(PYTHON) setup.py sdist

clean:
	rm -rf build systemd/*.so systemd/*.py[co] *.py[co] systemd/__pycache__

distclean: clean
	rm -rf dist MANIFEST systemd/id128-constants.h

SPHINXOPTS = -D version=$(VERSION) -D release=$(VERSION)
sphinx-%: build
	PYTHONPATH=$(builddir) $(SPHINX_BUILD) -b $* $(SPHINXOPTS) docs build/$*
	@echo Output has been generated in build/docs

check: build
	$(PYTHON) -m py.test $(builddir) docs $(TESTFLAGS)

TAGS: $(shell git ls-files systemd/*.[ch])
	$(ETAGS) $+

.PHONY: build install dist clean distclean TAGS
