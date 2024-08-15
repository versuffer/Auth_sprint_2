check:
	isort . --check-only
	flake8
	mypy .
	bandit -c pyproject.toml -r .

format:
	isort .
	black .
	flake8
