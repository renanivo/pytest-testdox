import sys
from typing import Generator

import pytest

try:
    from pytest import CallInfo, Config, Parser, TestReport  # type: ignore
except ImportError:  # For pytest < 7.0.0
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo

from pytest import Item

from pytest_testdox import constants, terminal


def pytest_addoption(parser: Parser):
    group = parser.getgroup('terminal reporting', 'reporting', after='general')
    group.addoption(
        '--testdox',
        action='store_true',
        dest='testdox',
        default=False,
        help='Report test progress in testdox format',
    )
    group.addoption(
        '--force-testdox',
        action='store_true',
        dest='force_testdox',
        default=False,
        help='Force testdox output even when not in real terminal',
    )
    parser.addini(
        'testdox_format',
        help='TestDox report format (plaintext|utf8)',
        default='utf8',
    )
    group.addoption(
        '--testdox-group-params',
        action='store_true',
        default=None,
        help='Group parametrized cases under their test title',
    )
    group.addoption(
        '--no-testdox-group-params',
        action='store_false',
        dest='testdox_group_params',
        default=None,
        help='Show parametrized cases with the full test title on each line',
    )
    parser.addini(
        'testdox_group_params',
        help='Group parametrized cases under their test title',
        type='bool',
        default=True,
    )


def should_enable_plugin(config: Config):
    return (
        config.option.testdox and sys.stdout.isatty()
    ) or config.option.force_testdox


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    config.addinivalue_line(
        "markers",
        "{}(title): Override testdox report test title".format(
            constants.TITLE_MARK
        ),
    )
    config.addinivalue_line(
        "markers",
        "{}(title): Override testdox report class title".format(
            constants.CLASS_NAME_MARK
        ),
    )

    if should_enable_plugin(config):
        # Get the standard terminal reporter plugin and replace it with ours
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        testdox_reporter = terminal.TestdoxTerminalReporter(
            standard_reporter.config
        )
        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(testdox_reporter, 'terminalreporter')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item, call: CallInfo
) -> Generator[None, TestReport, None]:
    result = yield

    report = result.get_result()

    if hasattr(item, 'callspec'):
        report.testdox_param_id = item.callspec.id
        report.testdox_group_id = item.nodeid.removesuffix(
            '[{}]'.format(item.callspec.id)
        )

    testdox_title = next(
        (
            mark.args[0]
            for mark in item.iter_markers(name=constants.TITLE_MARK)
        ),
        None,
    )
    testdox_class_name = next(
        (
            mark.args[0]
            for mark in item.iter_markers(name=constants.CLASS_NAME_MARK)
        ),
        None,
    )
    if testdox_title:
        report.testdox_title = testdox_title

    if testdox_class_name:
        report.testdox_class_name = testdox_class_name
