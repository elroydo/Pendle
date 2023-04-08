setup:
	pip install -r requirements.txt

install: clean
	python setup.py install

run:
	python donna/main.py

test:
	python -m pytest -x pendle/tests

venvactivate:
	py.test tests

clean:
	rm -rf pendle/__pycache__