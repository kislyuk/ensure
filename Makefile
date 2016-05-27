SHELL=/bin/bash

env: requirements.txt
	virtualenv env
	source env/bin/activate; pip install --requirement=requirements.txt

lint:
	env/bin/python setup.py flake8

test: env lint
	env/bin/python setup.py test -v

release: docs
	python setup.py sdist bdist_wheel upload -s -i D2069255

init_docs:
	cd docs; sphinx-quickstart

docs:
	$(MAKE) -C docs html

install:
	./setup.py install

.PHONY: test release docs
