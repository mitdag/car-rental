install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	pytest

format:
	ruff format

refactor: 
	format lint

lint:
	#pylint --disable=R,C --ignore-patterns=test_.*?py *.py app/*.py
	#ruff linting is faster than pylpyint
	ruff check *.py app/*.py

all: install lint test format