PYTHON = python
SED = sed
SPHINX_BUILD = sphinx-build
INCLUDE_DIR = /usr/include/
VERSION := $(shell $(PYTHON) setup.py --version)

define buildscript
import sys,sysconfig
print("build/lib.{}-{}.{}".format(sysconfig.get_platform(), *sys.version_info[:2]))
endef

builddir := $(shell $(PYTHON) -c '$(buildscript)')

all: build

systemd/id128-constants.h: $(INCLUDE_DIR)/systemd/sd-messages.h
	$(SED) -n -r 's/,//g; s/#define (SD_MESSAGE_[A-Z0-9_]+)\s.*/add_id(m, "\1", \1) JOINER/p' <$< >$@

build: systemd/id128-constants.h
	$(PYTHON) setup.py build

SPHINXOPTS = -D version=$(VERSION) -D release=$(VERSION)
sphinx-%: build
	PYTHONPATH=$(builddir) $(SPHINX_BUILD) -b $* $(SPHINXOPTS) docs build/docs
	@echo Output has been generated in build/docs

.PHONY: build
