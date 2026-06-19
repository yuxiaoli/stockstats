# Repository Guidelines

## Project Structure & Module Organization

This repository is a compact Python package built around a single module:

- `src/stockstats.py`: library source, including `StockDataFrame`, indicator parsing, and indicator calculation handlers.
- `test.py`: pytest test suite for indicators and compatibility behavior.
- `test_data/`: local CSV fixtures used by tests.
- `requirements.txt`: runtime dependencies (`numpy`, `pandas`).
- `test-requirements.txt`: test and lint dependencies.
- `pyproject.toml` and `tox.ini`: build metadata, pytest settings, coverage command, and flake8 command.

Keep new source behavior in `src/stockstats.py` unless the package is intentionally restructured. Add or update fixtures in `test_data/` when tests need deterministic market data.

## Build, Test, and Development Commands

```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
pytest --cov=src test.py
pytest test.py::StockDataFrameTest::test_get_rsi -v
flake8 src/ test.py
tox
```

- Install both requirements files before running the full test suite.
- `pytest --cov=src test.py` runs all tests with coverage.
- The single-test form is useful while developing one indicator.
- `flake8 src/ test.py` checks style.
- `tox` runs the configured environments from `tox.ini`.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation and flake8-clean code. The package supports Python 3.9+ per `pyproject.toml`; avoid syntax that would raise this minimum without an explicit project decision.

Indicator implementations follow existing naming patterns:

- Handler methods use `_get_<indicator>(self, meta)`, for example `_get_rsi`.
- Default windows live in `_dft_windows`.
- Default source columns live in `_dft_column`.
- Multi-column indicators should be registered in the `handler` property mapping.

Preserve the column-expression conventions documented in `CLAUDE.md`, such as `rsi_14`, `close_20_sma`, `close_delta`, and cross/comparison patterns.

## Testing Guidelines

tests use pytest plus PyHamcrest assertions. Add tests in `test.py` near related indicator coverage and name methods `test_<behavior>`. Prefer deterministic fixture data from `test_data/`; avoid introducing new live network dependencies unless compatibility behavior requires it. Run `pytest --cov=src test.py` and `flake8 src/ test.py` before submitting changes.

## Commit & Pull Request Guidelines

Recent commits use short, imperative or descriptive messages, for example `Fix _tp() to always return pandas Series` and `Update GitHub Sponsors username in FUNDING.yml`. Keep commits focused on one behavioral change.

Pull requests should include a concise description, linked issues when applicable, test results, and notes for user-visible indicator behavior changes. Screenshots are usually unnecessary for this library.

## Security & Configuration Tips

Do not commit generated caches, virtual environments, coverage output, or downloaded market data. Keep dependency changes explicit in `requirements.txt`, `test-requirements.txt`, or `pyproject.toml`.
