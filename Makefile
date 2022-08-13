PYTHON = python
SED = sed
ETAGS = etags
INCLUDE_DIR := $(shell pkg-config --variable=includedir libsystemd)
INCLUDE_FLAGS := $(shell pkg-config --cflags libsystemd)
VERSION := $(shell $(PYTHON) setup.py --version)
TESTFLAGS = -v

define buildscript
import sys, sysconfig, setuptools
sversion = int(setuptools.__version__.split(".")[0])
end = sys.implementation.cache_tag if sversion >= 61 else "{}.{}".format(*sys.version_info[:2])
print("build/lib.{}-{}".format(sysconfig.get_platform(), end))
endef

builddir := $(shell $(PYTHON) -c '$(buildscript)')

all: build

.PHONY: update-constants
update-constants: update-constants.py $(INCLUDE_DIR)/systemd/sd-messages.h
	$(PYTHON) $+ systemd/id128-defines.h | \
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
	$(PYTHON) setup.py build_ext $(INCLUDE_FLAGS)
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install --skip-build $(if $(DESTDIR),--root $(DESTDIR))

dist:
	$(PYTHON) setup.py sdist

sign: dist/systemd-python-$(VERSION).tar.gz
	gpg --detach-sign -a dist/systemd-python-$(VERSION).tar.gz

clean:
	rm -rf build systemd/*.so systemd/*.py[co] *.py[co] systemd/__pycache__

distclean: clean
	rm -rf dist MANIFEST

SPHINXOPTS += -D version=$(VERSION) -D release=$(VERSION)
sphinx-%: build
	cd build && \
	  PYTHONPATH=../$(builddir) $(PYTHON) -m sphinx -b $* $(SPHINXOPTS) ../docs $*
	@echo Output has been generated in build/$*

doc: sphinx-html

check: build
	(cd $(builddir) && $(PYTHON) -m pytest . ../../docs $(TESTFLAGS))

www_target = www.freedesktop.org:/srv/www.freedesktop.org/www/software/systemd/python-systemd
doc-sync:
	rsync -rlv --delete --omit-dir-times build/html/ $(www_target)/

upload: dist/systemd-python-$(VERSION).tar.gz dist/systemd-python-$(VERSION).tar.gz.asc
	twine-3 upload $+

TAGS: $(shell git ls-files systemd/*.[ch])
	$(ETAGS) $+

shell:
# we change the directory because python insists on adding $CWD to path
	(cd $(builddir) && $(PYTHON))

.PHONY: build install dist sign upload clean distclean TAGS doc doc-sync shell
