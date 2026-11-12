# Canonical Store Api - Python package

[![Test live APIs](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/workflows/Test%20live%20APIs/badge.svg)](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/actions?query=workflow%3ATest%20live%20APIs)
[![Tests](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/workflows/Tests/badge.svg)](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/actions?query=workflow%3A)
[![Publish](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/workflows/Publish/badge.svg)](https://github.com/canonical-web-and-design/canonicalwebteam.store-api/actions?query=workflow%3APublish)
[![Code coverage](https://codecov.io/gh/canonical-web-and-design/canonicalwebteam.store-api/branch/main/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/canonicalwebteam.store-api)

## How to install

To install this extension as a requirement in your project, you can use PIP:

```bash
pip install canonicalwebteam.store-api
```

See also the documentation for [pip install](https://pip.pypa.io/en/stable/reference/pip_install/).

## Development

The package leverages [poetry](https://poetry.eustace.io/) for dependency management.
Install the development dependencies, including coverage and mypy, with:

```bash
poetry install --with dev
```

## Testing

All tests can be run with `poetry run python3 -m unittest discover tests`.

To measure coverage and check type hints using the development dependencies:

```bash
poetry run coverage run --source=. -m unittest discover tests
poetry run coverage xml
poetry run mypy canonicalwebteam/store_api --follow-untyped-imports
```

To build the package and verify that the wheel requires only runtime dependencies:

```bash
poetry build
python3 tests/check_wheel_metadata.py dist/*.whl
```
