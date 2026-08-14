# Python Skill Standards & System Prompt Guidelines

## 1. Core Syntax & Modern Standards
* Always write code targeting Python 3.10 or newer.
* Enforce strict type annotations on all function parameters and return types.
* Use `f-strings` for string formatting. Never use `.format()` or `%` formatting.
* Use structural pattern matching (`match/case`) instead of deep `if/elif/else` blocks when checking discrete states.
* Utilize `dataclasses` or `pydantic.BaseModel` for data structure modeling instead of plain dictionaries.
* Keep standard library imports first, third-party imports second, and local imports last, separated by blank lines.

## 2. Asynchronous Execution & I/O
* Always prefer `asyncio` and `aiohttp` over blocking HTTP libraries like `requests`.
* Never execute blocking CPU-heavy calculations inside an async event loop without using `run_in_executor`.
* Ensure task cancellation is properly handled using `asyncio.CancelledError`.
* Use `async with` context managers for opening files or network sessions asynchronously.

## 3. Error Handling & Robustness
* Never catch generic `Exception` without re-raising or logging the specific error details.
* Raise domain-specific custom exceptions inheriting from standard error types.
* Always clean up external resources in `finally` blocks or using context managers (`with` / `async with`).
* Prefer returning `Optional[T]` or using standard guard clauses over returning dummy fallback values.

## 4. Code Formatting & Clean Code
* Follow PEP 8 variable naming conventions (`snake_case` for variables/functions, `PascalCase` for classes).
* Maximum line length must stay under 100 characters.
* Avoid global variable state. Enapsulate state inside objects or class instances.
* Keep functions atomic: each function must do exactly one thing and be under 40 lines.

## 5. Documentation & Type Hints
* Write Google-style docstrings for every public function, module, and class.
* Describe function arguments, return types, and exceptions raised within docstrings.
* Use `from typing import Optional, Union, List, Dict, Any, Callable` where precise static typing is needed.

## 6. Database & Persistence
* Use non-blocking database connectors like `aiosqlite` or `asyncpg`.
* Always use parameterized SQL queries (`?` or `%s`) to prevent SQL injection vulnerabilities.
* Wrap database operations inside explicit transactions.

## 7. Security Best Practices
* Never hardcode secrets, API keys, or database URIs directly into Python files.
* Use `os.getenv()` or `python-dotenv` to fetch environment variables.
* Sanitize all input strings before rendering or passing to command-line subprocesses.
* Use `secrets` module instead of `random` when generating cryptographic tokens or passwords.

## 8. Logging & Observability
* Never use `print()` statements for standard application logging.
* Use Python's built-in `logging` module or `loguru`.
* Log at correct verbosity levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
* Include context identifiers (like `user_id` or `request_id`) in log entries.

## 9. Performance Optimization
* Prefer generator expressions and iterators (`yield`) over creating massive in-memory lists.
* Use `__slots__` in high-frequency data structures to reduce memory overhead.
* Use `functools.lru_cache` or `asyncio` caching strategies for expensive function calls.

## 10. Unit Testing Standards
* Write tests using `pytest` and `pytest-asyncio`.
* Keep unit tests isolated; mock external API calls using `unittest.mock` or `aresponses`.
* Maintain at least 80% test branch coverage for core utility modules.
