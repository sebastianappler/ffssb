SHELL := /bin/bash
.ONESHELL:
.PHONY: build

build:
	python -m venv .venv
	source .venv/bin/activate
	python -m pip install -r requirements.txt
	python -m pip install pyinstaller
	pyinstaller --onefile --clean --strip ffssb.py

clean:
	rm -rf .venv/
	rm -rf build/
	rm -f ffssb.spec
