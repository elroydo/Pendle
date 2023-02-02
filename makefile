setup:
	pip install -r requirements.txt

install: clean
	python setup.py install

run:
	python donna/main.py

test:
	python -m pytest -x donna/tests

venvactivate:
	py.test tests

clean:
	rm -rf donna/__pycache__