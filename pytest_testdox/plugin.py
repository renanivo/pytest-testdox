# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

import pytest
from _pytest.terminal import TerminalReporter

from . import constants, models, wrappers


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting', 'reporting', after='general')
    group.addoption(
        '--testdox', action='store_true', dest='testdox', default=False,
        help='Report test progress in testdox format'
    )
    group.addoption(
        '--force-testdox', action="store_true",
        dest="force_testdox", default=False,
        help=(
            "Force testdox output even when not in real terminal"
        )
    )
    parser.addini(
        'testdox_format',
        help='TestDox report format (plaintext|utf8)',
        default='utf8'
    )


def should_enable_plugin(config):
    return (
        (config.option.testdox and sys.stdout.isatty())
        or config.option.force_testdox
    )


@pytest.mark.trylast
def pytest_configure(config):
    if should_enable_plugin(config):
        # Get the standard terminal reporter plugin and replace it with ours
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        testdox_reporter = TestdoxTerminalReporter(standard_reporter.config)
        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(testdox_reporter, 'terminalreporter')
        config.addinivalue_line(
            "markers",
            "{}(title): Override testdox report test title".format(
                constants.TITLE_MARK
            )
        )
        config.addinivalue_line(
            "markers",
            "{}(title): Override testdox report class title".format(
                constants.CLASS_NAME_MARK
            )
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield

    report = result.get_result()

    testdox_title = _first(
        mark.args[0]
        for mark in item.iter_markers(name=constants.TITLE_MARK)
    )
    testdox_class_name = _first(
        mark.args[0]
        for mark in item.iter_markers(name=constants.CLASS_NAME_MARK)
    )
    if testdox_title:
        report.testdox_title = testdox_title

    if testdox_class_name:
        report.testdox_class_name = testdox_class_name


class TestdoxTerminalReporter(TerminalReporter):

    def __init__(self, config, file=None):
        TerminalReporter.__init__(self, config, file)
        self._last_header = None
        self.pattern_config = models.PatternConfig(
            files=self.config.getini('python_files'),
            functions=self.config.getini('python_functions'),
            classes=self.config.getini('python_classes')
        )
        self.result_wrappers = []

        if config.getini('testdox_format') != 'plaintext':
            self.result_wrappers.append(wrappers.UTF8Wrapper)

        if config.option.color != 'no':
            self.result_wrappers.append(wrappers.ColorWrapper)

    def _register_stats(self, report):
        """
        This method is not created for this plugin, but it is needed in order
        to the reporter display the tests summary at the end.

        Originally from:
        https://github.com/pytest-dev/pytest/blob/47a2a77/_pytest/terminal.py#L198-L201
        """
        res = self.config.hook.pytest_report_teststatus(
            report=report,
            config=self.config
        )
        category = res[0]
        self.stats.setdefault(category, []).append(report)
        self._tests_ran = True

    def pytest_runtest_logreport(self, report):
        self._register_stats(report)

        if report.when != 'call' and not report.skipped:
            return

        result = models.Result.create(report, self.pattern_config)

        for wrapper in self.result_wrappers:
            result = wrapper(result)

        if result.header != self._last_header:
            self._last_header = result.header
            self._tw.sep(' ')
            self._tw.line(result.header)

        try:
            self._tw.line(unicode(result))
        except NameError:
            self._tw.line(str(result))


def _first(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return None
