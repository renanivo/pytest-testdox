import sys
from typing import Generator, List, Optional, TextIO, Tuple

import pytest

if pytest.__version__ < '7.0.0':
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo
else:
    from pytest import Config, Parser, TestReport, CallInfo

from _pytest.terminal import TerminalReporter
from pytest import Item

from pytest_testdox import constants, models, wrappers


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


def should_enable_plugin(config: Config):
    return (
        config.option.testdox and sys.stdout.isatty()
    ) or config.option.force_testdox


@pytest.mark.trylast
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
        testdox_reporter = TestdoxTerminalReporter(standard_reporter.config)
        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(testdox_reporter, 'terminalreporter')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item, call: CallInfo
) -> Generator[None, TestReport, None]:
    result = yield

    report = result.get_result()

    testdox_title = _first(
        mark.args[0] for mark in item.iter_markers(name=constants.TITLE_MARK)
    )
    testdox_class_name = _first(
        mark.args[0]
        for mark in item.iter_markers(name=constants.CLASS_NAME_MARK)
    )
    if testdox_title:
        report.testdox_title = testdox_title

    if testdox_class_name:
        report.testdox_class_name = testdox_class_name


class TestdoxTerminalReporter(TerminalReporter):  # type: ignore
    def __init__(self, config: Config, file: TextIO = None):
        super().__init__(config, file)
        self._last_header_id: Optional[str] = None
        self.pattern_config = models.PatternConfig(
            files=self.config.getini('python_files'),
            functions=self.config.getini('python_functions'),
            classes=self.config.getini('python_classes'),
        )
        self.result_wrappers: List[type] = []

        if config.getini('testdox_format') != 'plaintext':
            self.result_wrappers.append(wrappers.UTF8Wrapper)

        if config.option.color != 'no':
            self.result_wrappers.append(wrappers.ColorWrapper)

    def _register_stats(self, report: TestReport):
        """
        This method is not created for this plugin, but it is needed in order
        to the reporter display the tests summary at the end.

        Originally from:
        https://github.com/pytest-dev/pytest/blob/47a2a77/_pytest/terminal.py#L198-L201
        """
        res = self.config.hook.pytest_report_teststatus(
            report=report, config=self.config
        )
        category = res[0]
        self.stats.setdefault(category, []).append(report)
        self._tests_ran = True

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        self._register_stats(report)

        if report.when != 'call' and not report.skipped:
            return

        result = models.Result.create(report, self.pattern_config)

        for wrapper in self.result_wrappers:
            result = wrapper(result)

        if result.header_id != self._last_header_id:
            self._last_header_id = result.header_id
            self._tw.sep(' ')
            self._tw.line(result.header)

        self._tw.line(str(result))

    def pytest_runtest_logstart(
        self, nodeid: str, location: Tuple[str, Optional[int], str]
    ) -> None:
        # Ensure that the path is printed before the
        # 1st test of a module starts running.
        self.write_fspath_result(nodeid, '')

        # To support Pytest < 6.0.0
        if hasattr(self, 'flush'):
            self.flush()


def _first(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return None
