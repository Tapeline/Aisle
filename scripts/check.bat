coverage run -m pytest tests
if %errorlevel% neq 0 exit /b %errorlevel%
coverage html
mypy aisle
if %errorlevel% neq 0 exit /b %errorlevel%
ruff check
if %errorlevel% neq 0 exit /b %errorlevel%
flake8 aisle tests
if %errorlevel% neq 0 exit /b %errorlevel%
lint-imports
if %errorlevel% neq 0 exit /b %errorlevel%

echo All checks passed