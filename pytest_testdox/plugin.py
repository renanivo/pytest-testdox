# -*- coding: utf-8 -*-
import re

import pytest
from _pytest.terminal import TerminalReporter

from . import formatters


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

    def pytest_runtest_logstart(self, nodeid, location):
        pass

    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return

        node_parts = report.nodeid.split('::')

        title = node_parts[-1]
        class_name = node_parts[-3] if '()' in node_parts[-2] else ''
        module_name = node_parts[0]

        if class_name:
            header = formatters.format_class_name(class_name)
        else:
            header = formatters.format_module_name(module_name)

        if header != self._last_header:
            self._last_header = header
            self._tw.sep(' ')
            self._tw.line(header)

        self._tw.line('- [{outcome}] {title}'.format(
            outcome=formatters.format_outcome(report.outcome),
            title=formatters.format_title(title)
        ))
