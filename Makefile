SHELL ?= /bin/sh
PYTHON_BIN ?= python

.PHONY: build

build:
	$(PYTHON_BIN) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install pyinstaller
	. .venv/bin/activate && pyinstaller --onefile --clean --strip ffssb.py

clean:
	rm -rf .venv/
	rm -rf build/
	rm -rf dist/
	rm -f ffssb.spec

install:
	install -m 755 dist/ffssb /usr/local/bin
