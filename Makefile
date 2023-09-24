#!/usr/bin/make -f
##
# Makefile for Debian Package Checker (Review System)
##

# Run local application
app:
	python3 -m dcheck.app

web:
	#TODO

docs:
	make -C docs html
	sensible-browser docs/_build/html/index.html

test:
	python3 -m pytest

# Clean up build/cache data
clean:
	# Python cache
	find . -name '*.pyc' \
		-o -type d -name '__pycache__' \
		-o -type d -name '.pytest_cache' \
		-exec rm -rf {} \;
	# Sphinx-doc
	make -C docs clean

.PHONY: app web docs test clean
