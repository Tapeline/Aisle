coverage run -m pytest tests
coverage html
mypy aisle
ruff check
flake8 aisle tests
lint-imports
