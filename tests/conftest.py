# -*- coding: utf-8 -*-
import os
import warnings

import pytest

pytest_plugins = 'pytester'


@pytest.fixture(scope='session', autouse=True)
def verify_target_path():
    import pytest_testdox

    current_path_root = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )
    if current_path_root not in pytest_testdox.__file__:
        warnings.warn(
            'pytest-testdox was not imported from your repository. '
            'You might be testing the wrong code '
            '-- More: https://github.com/renanivo/pytest-testdox/issues/13',
            UserWarning
        )
