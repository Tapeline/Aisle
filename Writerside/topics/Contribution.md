# Contribution

We warmly welcome all contributors!

## First steps
1. Fork the repo
2. Clone the fork
3. Commit changes
4. Create a pull request
5. You're awesome!


## Running the local copy
> Prerequisite: installed Python 3.12+

Aisle manages dependencies with Poetry. Just install Poetry, then all dependencies:
```shell
pip install poetry
poetry install
```

You now should be able to run `aisle` command.


## Testing
Aisle uses following testing and checking tools:
- pytest + pytest-cov
- mypy
- ruff
- wemake-python-styleguide
- import-linter

Testing should be done as follows:
```shell
coverage -m run pytest tests
mypy aisle
ruff check
flake8 aisle tests
lint-imports
```

If you are on Windows, there is a prebuilt script `scripts/check.bat`.


## Guidelines and standards
There should be 0 warnings and errors by any of tools listed above + 100% test coverage.
