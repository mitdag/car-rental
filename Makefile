install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

install-uv:
	uv pip install -r requirements.txt

test:
	pytest

format:
	ruff format

refactor: 
	format lint

lint:
	#pylint --disable=R,C --ignore-patterns=test_.*?py *.py app/*.py
	#ruff linting is faster than pylpyint
	ruff check

all: install lint test format