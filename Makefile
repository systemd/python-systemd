# SPDX-License-Identifier: LGPL-2.1-or-later

PYTHON = python
SED = sed
ETAGS = etags
INCLUDE_DIR := $(shell pkg-config --variable=includedir libsystemd)
INCLUDE_FLAGS := $(shell pkg-config --cflags libsystemd)
VERSION := $(shell meson introspect --projectinfo build | jq -r .version)
TESTFLAGS = -v
BUILD_DIR = build

all: build

build:
	$(PYTHON) -m build -Cbuild-dir=$(BUILD_DIR)

install:
	$(PYTHON) -m pip install .

dist:
	$(PYTHON) -m build --sdist

sign: dist/systemd-python-$(VERSION).tar.gz
	gpg --detach-sign -a dist/systemd-python-$(VERSION).tar.gz

clean:
	rm -rf $(BUILD_DIR) systemd/*.so systemd/*.py[co] *.py[co] systemd/__pycache__

distclean: clean
	rm -rf dist MANIFEST

check: build install
	($(PYTHON) -m pytest src/systemd/test docs $(TESTFLAGS))

www_target = www.freedesktop.org:/srv/www.freedesktop.org/www/software/systemd/python-systemd
doc-sync:
	rsync -rlv --delete --omit-dir-times $(BUILD_DIR)/html/ $(www_target)/

upload: dist/systemd-python-$(VERSION).tar.gz dist/systemd-python-$(VERSION).tar.gz.asc
	twine-3 upload $+

TAGS: $(shell git ls-files systemd/*.[ch])
	$(ETAGS) $+

shell:
	$(PYTHON)

.PHONY: build install dist sign upload clean distclean TAGS doc doc-sync shell
