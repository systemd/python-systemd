PYTHON = python
SED = sed
ETAGS = etags
INCLUDE_DIR := $(shell pkg-config --variable=includedir libsystemd)
INCLUDE_FLAGS := $(shell pkg-config --cflags libsystemd)
VERSION := $(shell meson introspect --projectinfo build | jq -r .version)
TESTFLAGS = -v
BUILD_DIR = build

all: build

.PHONY: update-constants
update-constants: update-constants.py $(INCLUDE_DIR)/systemd/sd-messages.h
	$(PYTHON) $+ src/systemd/id128-defines.h | \
	  sort -u | \
	  tee src/systemd/id128-defines.h.tmp | \
	  $(SED) -n -r 's/,//g; s/#define (SD_MESSAGE_[A-Z0-9_]+)\s.*/add_id(m, "\1", \1) JOINER/p' | \
	  sort -u > src/systemd/id128-constants.h.tmp
	mv src/systemd/id128-defines.h{.tmp,}
	mv src/systemd/id128-constants.h{.tmp,}
	($(SED) 9q <docs/id128.rst && \
	  sed -n -r 's/#define (SD_MESSAGE_[A-Z0-9_]+) .*/   .. autoattribute:: systemd.id128.\1/p' \
	  src/systemd/id128-defines.h) >docs/id128.rst.tmp
	mv docs/id128.rst{.tmp,}

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

SPHINXOPTS += -D version=$(VERSION) -D release=$(VERSION)
sphinx-%: install
	mkdir $(BUILD_DIR) && cd $(BUILD_DIR) && $(PYTHON) -m sphinx -b $* $(SPHINXOPTS) ../docs $*
	@echo Output has been generated in $(BUILD_DIR)/$*

doc: sphinx-html

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
