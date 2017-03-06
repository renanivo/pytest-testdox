# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

    def pytest_runtest_logreport(self, report):
        res = self.config.hook.pytest_report_teststatus(report=report)
        category = res[0]
        self.stats.setdefault(category, []).append(report)
        self._tests_ran = True

        if report.when != 'call':
            return

        node = parsers.parse_node(report.nodeid)

        if node.class_name:
            header = node.class_name
        else:
            header = node.module_name

        if header != self._last_header:
            self._last_header = header
            self._tw.sep(' ')
            self._tw.line(header)

        self._tw.line('- [{outcome}] {title}'.format(
            outcome=formatters.format_outcome(report.outcome),
            title=node.title
        ))
