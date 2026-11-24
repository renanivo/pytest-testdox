import os
import warnings

import pytest

pytest_plugins = 'pytester'


@pytest.fixture
def testdir(testdir, monkeypatch):
    # Inner pytest runs load our plugin explicitly, without installed plugins.
    monkeypatch.setenv('PYTEST_DISABLE_PLUGIN_AUTOLOAD', '1')
    testdir.makeconftest("pytest_plugins = 'pytest_testdox.plugin'")
    return testdir


@pytest.fixture(scope='session', autouse=True)
def verify_target_path():
    import pytest_testdox

    current_path_root = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )
    if current_path_root not in pytest_testdox.__file__:
        warnings.warn(
            'pytest-testdox was not imported from your repository. '
            'You might be testing the wrong code. '
            'Uninstall pytest-testdox to be able to run all test cases '
            '-- More: https://github.com/renanivo/pytest-testdox/issues/13',
            UserWarning,
        )
