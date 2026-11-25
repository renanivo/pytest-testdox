import importlib.util
from pathlib import Path

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.reports import TestReport as PytestReport
from _pytest.runner import CallInfo

import pytest_testdox


@pytest.mark.parametrize(
    'module_name,expected_exports',
    [
        (
            'plugin',
            {
                'Config': Config,
                'TestReport': PytestReport,
                'Parser': Parser,
                'CallInfo': CallInfo,
            },
        ),
        ('terminal', {'Config': Config, 'TestReport': PytestReport}),
    ],
)
def test_modules_import_when_pytest_does_not_export_report_types(
    monkeypatch, module_name, expected_exports
):
    for name in expected_exports:
        monkeypatch.delattr(pytest, name, raising=False)

    path = Path(pytest_testdox.__file__).with_name(f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(
        f'testdox_legacy_{module_name}', path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name, expected_type in expected_exports.items():
        assert getattr(module, name) is expected_type
