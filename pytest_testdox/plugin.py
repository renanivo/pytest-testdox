# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import partial

import pytest
from _pytest.terminal import TerminalReporter

from . import formatters, parsers


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

    _last_header = ''

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

        pattern_config = parsers.PatternConfig(
            files=self.config.getini('python_files'),
            functions=self.config.getini('python_functions'),
            classes=self.config.getini('python_classes')
        )
        node = parsers.parse_node(report.nodeid, pattern_config)

        if node.class_name:
            header = node.class_name
        else:
            header = node.module_name

        if header != self._last_header:
            self._last_header = header
            self._tw.sep(' ')
            self._tw.line(header)

        colored = partial(formatters.colored, outcome=report.outcome)

        self._tw.line(colored('- [{outcome}] {title}'.format(
            outcome=formatters.format_outcome(report.outcome),
            title=node.title
        )))
