.PHONY: all build install test

all:
	make build
	make install
	make test



build:
	rm -rf build/ sdist/ dist/ gsio-*/ gsio.egg-info/
	python setup.py sdist build
	python setup.py bdist_wheel --universal
	twine check dist/*

install:
	python setup.py install --user

travisinstall:
	python setup.py install

test:
	bash -c "export PYTHONPATH="$(PYTHONPATH):$(PWD)"; coverage run --source gsio ./tests/test.py" 
	echo `which gsio`
	# coverage run --source gsio `which gsio` -h
	# coverage run --source gsio `which gsio` LISTSUBCOMMAND
	# coverage run --source gsio `which gsio` LISTSUBCOMMAND | xargs -n 1 -I [] bash -c '(coverage run --source gsio `which gsio` [] -h >/dev/null 2>&1 || echo ERROR: [])'
	coverage report -m

test_env:
	bash -c ' \
	rm -rf venv; \
	virtualenv venv; \
	source venv/bin/activate; \
	which python; \
	python --version; \
	pip install -r requirements.txt; \
	make build; \
	make travisinstall; \
	make test'
	
upload:
	twine upload dist/*

clean:
	rm -rf venv build *.egg-info dist
