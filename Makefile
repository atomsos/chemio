.PHONY: all build install test

all:
	make build
	make install
	make test



build:
	rm -rf build/ sdist/ dist/ chemio-*/ chemio.egg-info/
	python setup.py sdist build
	python setup.py bdist_wheel --universal
	twine check dist/*

install:
	cd /tmp; pip uninstall -yy chemio; cd -; python setup.py install --user

travisinstall:
	python setup.py install

test:
	bash -c "export PYTHONPATH="$(PYTHONPATH):$(PWD)"; coverage run --source chemio ./tests/test.py" 
	echo `which chemio`
	# coverage run --source chemio `which chemio` -h
	# coverage run --source chemio `which chemio` LISTSUBCOMMAND
	# coverage run --source chemio `which chemio` LISTSUBCOMMAND | xargs -n 1 -I [] bash -c '(coverage run --source chemio `which chemio` [] -h >/dev/null 2>&1 || echo ERROR: [])'
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
