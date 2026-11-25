# pytest-testdox

[![PyPI](https://img.shields.io/pypi/v/pytest-testdox.svg?color=brightgreen)](https://pypi.org/project/pytest-testdox/)
[![Continuous Integration Status](https://github.com/renanivo/pytest-testdox/workflows/Continuous%20Integration/badge.svg)](https://github.com/renanivo/pytest-testdox/actions?query=workflow%3A%22Continuous+Integration%22)
[![codecov](https://codecov.io/gh/renanivo/pytest-testdox/branch/master/graph/badge.svg)](https://codecov.io/gh/renanivo/pytest-testdox)

A [TestDox format](https://en.wikipedia.org/wiki/TestDox) reporter for pytest.

![](https://i.imgur.com/rJRL4x9.png)

## Install

Requires Python 3.11 or newer. CI covers CPython through 3.15, including
the free-threaded 3.14t and 3.15t builds, and pytest 9 or newer alongside
older pytest versions where compatible.

```
pip install pytest-testdox
```

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv sync --locked
make check test
```

`make check` runs Pyrefly, Ruff lint, and Ruff's formatting check. Use
`make format` to format code and sort imports. `uv.lock` pins development
dependencies; run `uv lock --upgrade` to update them.

Build the wheel and source distribution with `uv build` (or `make build`).
The artifacts are written to `dist/`.

## Usage

Add the parameter `--testdox` when running `pytest`. For example:

```sh
pytest --testdox your-tests/
```

Tip: If you don't want to type `--testdox` every time you run `pytest`, add it
to [`addopts`](https://docs.pytest.org/en/latest/customize.html#confval-addopts)
in your [ini file](https://docs.pytest.org/en/latest/customize.html#initialization-determining-rootdir-and-inifile).
For example:

```ini
# content of pytest.ini or tox.ini
[pytest]
addopts = --testdox

# or if you use setup.cfg
[tool:pytest]
addopts = --testdox
```

When using `--testdox`, the plugin will disable itself when not running on a
terminal. If you want the testdox report no matter what, use the parameter
`--force-testdox` instead.


## Parametrized tests

Parametrized cases are grouped under their test title by default when
running `pytest --testdox`:

```python
@pytest.mark.parametrize('parameter', ['blue', 'yellow', 'green'])
def test_passes_with_parameters(parameter):
    assert True
```

```text
   passes with parameters
    ✓ blue
    ✓ yellow
    ✓ green
```

Each case keeps its own result indicator. The parent title has no result
indicator. Custom parameter IDs and `@pytest.mark.it` titles are supported.
To show the full test title on each case instead, run
`pytest --testdox --no-testdox-group-params` or disable grouping in configuration:

```ini
[pytest]
testdox_group_params = false
```

Use `--testdox-group-params` to enable grouping even when configuration
disables it. Command-line options take precedence over configuration.
These options control formatting; enable the reporter with `--testdox` or
`--force-testdox` as usual.

## Markers

### @pytest.mark.describe

Override the class name in the testdox report. For example:

```python
# test_demo.py
@pytest.mark.describe('create_file')
class TestCreateFile:
    def test_creates_a_file_in_the_so(self):
        pass
```

Will produce the output:

```
test_demo.py

create_file
 [x] creates a file in the so
```

### @pytest.mark.it

Override the test title in the testdox report. For example:

```python
# test_demo.py
class TestCreateFile:
    @pytest.mark.it('Creates a local file in the SO')
    def test_creates_a_file_in_the_so(self):
        pass
```

Will produce the output:


```
test_demo.py

Create File
 [x] Creates a local file in the SO
```

## Configuration file options

### testdox_format

Specifies TestDox report format, `plaintext` or `utf8` (default:
`utf8`). For example:

```ini
# content of pytest.ini
# (or tox.ini or setup.cfg)
[pytest]
testdox_format = plaintext
```

```console
$ pytest test_demo.py
============================= test session starts ==============================
platform darwin -- Python 3.5.0, pytest-3.0.7, py-1.4.33, pluggy-0.4.0
rootdir: /private/tmp/demo, inifile: pytest.ini
plugins: testdox-dev
collected 2 items

test_demo.py
Pytest Testdox
 [x] prints a BDD style output to your tests
 [x] lets you focus on the behavior
```
