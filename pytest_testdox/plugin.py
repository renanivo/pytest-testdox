# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from _pytest.terminal import TerminalReporter

from . import models


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting', 'reporting', after='general')
    group.addoption(
        '--testdox', action='store_true', dest='testdox', default=False,
        help='Report test progress in testdox format'
    )


@pytest.mark.trylast
def pytest_configure(config):
    if config.option.testdox:
        # Get the standard terminal reporter plugin and replace it with ours
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        testdox_reporter = TestdoxTerminalReporter(standard_reporter.config)
        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(testdox_reporter, 'terminalreporter')


class TestdoxTerminalReporter(TerminalReporter):

    def __init__(self, config, file=None):
        TerminalReporter.__init__(self, config, file)
        self._last_header = None
        self.pattern_config = models.PatternConfig(
            files=self.config.getini('python_files'),
            functions=self.config.getini('python_functions'),
            classes=self.config.getini('python_classes')
        )

    def _register_stats(self, report):
        """
        This method is not created for this plugin, but it is needed in order
        to the reporter display the tests summary at the end.

        Originally from:
        https://github.com/pytest-dev/pytest/blob/47a2a77/_pytest/terminal.py#L198-L201
        """
        res = self.config.hook.pytest_report_teststatus(report=report)
        category = res[0]
        self.stats.setdefault(category, []).append(report)
        self._tests_ran = True

    def pytest_runtest_logreport(self, report):
        self._register_stats(report)

        if report.when != 'call':
            return

        result = models.Result.create(report, self.pattern_config)

        if result.header != self._last_header:
            self._last_header = result.header
            self.write_sep(' ')
            self.write_line(result.header)

        result.use_colors = self.config.option.color != 'no'

        self.write_line(unicode(result))
