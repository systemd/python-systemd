PYTHON = python
SED = sed
SPHINX_BUILD = sphinx-build
ETAGS = etags
INCLUDE_DIR := $(shell pkg-config --variable=includedir libsystemd)
VERSION := $(shell $(PYTHON) setup.py --version)
TESTFLAGS = -v

define buildscript
import sys,sysconfig
print("build/lib.{}-{}.{}".format(sysconfig.get_platform(), *sys.version_info[:2]))
endef

builddir := $(shell $(PYTHON) -c '$(buildscript)')

all: build

.PHONY: update-constants
update-constants: $(INCLUDE_DIR)/systemd/sd-messages.h
	cat $< systemd/id128-defines.h | \
	  $(SED) -n -r '/#define SD_MESSAGE_[A-Z0-9_]/p' | \
	  sort -u | \
	  tee systemd/id128-defines.h.tmp | \
	  $(SED) -n -r 's/,//g; s/#define (SD_MESSAGE_[A-Z0-9_]+)\s.*/add_id(m, "\1", \1) JOINER/p' | \
	  sort -u >systemd/id128-constants.h.tmp
	mv systemd/id128-defines.h{.tmp,}
	mv systemd/id128-constants.h{.tmp,}
	($(SED) 9q <docs/id128.rst && \
	  sed -n -r 's/#define (SD_MESSAGE_[A-Z0-9_]+) .*/   .. autoattribute:: systemd.id128.\1/p' \
	  systemd/id128-defines.h) >docs/id128.rst.tmp
	mv docs/id128.rst{.tmp,}

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install --skip-build $(if $(DESTDIR),--root $(DESTDIR))

dist:
	$(PYTHON) setup.py sdist

clean:
	rm -rf build systemd/*.so systemd/*.py[co] *.py[co] systemd/__pycache__

distclean: clean
	rm -rf dist MANIFEST

SPHINXOPTS = -D version=$(VERSION) -D release=$(VERSION)
sphinx-%: build
	PYTHONPATH=$(builddir) $(SPHINX_BUILD) -b $* $(SPHINXOPTS) docs build/$*
	@echo Output has been generated in build/$*

check: build
	(cd $(builddir) && $(PYTHON) -m pytest . ../../docs $(TESTFLAGS))

www_target = www.freedesktop.org:/srv/www.freedesktop.org/www/software/systemd/python-systemd
doc-sync:
	rsync -rlv --delete --omit-dir-times build/html/ $(www_target)/

TAGS: $(shell git ls-files systemd/*.[ch])
	$(ETAGS) $+

.PHONY: build install dist clean distclean TAGS doc-sync
