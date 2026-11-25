import os

import pytest

from pytest_testdox.data_structures import Node, Result
from pytest_testdox.wrappers import ColorWrapper, UTF8Wrapper


@pytest.mark.parametrize(
    'outcome,expected',
    [
        ('passed', '\033[92m [x] title\033[0m'),
        ('failed', '\033[91m [ ] title\033[0m'),
        ('skipped', '\033[93m >>> title\033[0m'),
        ('unknown', '>>>title'),
    ],
)
def test_color_wrapper_formats_outcomes(outcome, expected):
    result = Result(outcome, Node('module', 'title', None))

    assert str(ColorWrapper(result)) == expected


@pytest.mark.parametrize(
    'outcome,expected',
    [
        ('passed', ' ✓ title'),
        ('failed', ' ✗ title'),
        ('skipped', ' » title'),
        ('unknown', ' » title'),
    ],
)
def test_utf8_wrapper_formats_outcomes(outcome, expected):
    result = Result(outcome, Node('module', 'title', None))

    assert str(UTF8Wrapper(result)) == expected


def test_combined_wrappers_preserve_headers_and_multiline_indentation():
    node = Node('module', f'first{os.linesep}second', 'Class')
    result = ColorWrapper(UTF8Wrapper(Result('passed', node)))

    assert result.header == 'Class'
    assert result.header_id == 'moduleClass'
    assert str(result) == f'\033[92m ✓ first{os.linesep}   second\033[0m'
