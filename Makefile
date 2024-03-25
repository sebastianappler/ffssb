SHELL ?= /bin/sh
PYTHON_BIN ?= python

.ONESHELL:
.PHONY: build

build:
	$(PYTHON_BIN) -m pip install -r requirements.txt
	$(PYTHON_BIN) -m pip install pyinstaller
	pyinstaller --onefile --clean --strip ffssb.py

build-venv:
	$(PYTHON_BIN) -m venv .venv
	source .venv/bin/activate
	make build

clean:
	rm -rf build/
	rm -rf dist/
	rm -f ffssb.spec

clean-venv: clean
	rm -rf .venv/

install:
	install -m 755 dist/ffssb /usr/local/bin
