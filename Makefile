PYTHON := `which python`

.PHONY: package build install clean

package:
	$(PYTHON) setup.py sdist --formats=gztar bdist_wheel

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

upload:
	twine upload dist/*
