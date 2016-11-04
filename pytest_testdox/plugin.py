# -*- coding: utf-8 -*-
import re

import pytest
from _pytest.terminal import TerminalReporter


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

    _last_class_name = None

    def pytest_runtest_logstart(self, nodeid, location):
        pass

    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return

        node_parts = report.nodeid.split('::')

        outcome = 'x' if report.outcome == 'passed' else ' '
        title = node_parts[-1]
        class_name = node_parts[-3] if '()' in node_parts[-2] else None

        if class_name != self._last_class_name:
            self._last_class_name = class_name
            self._tw.sep(' ')
            self._tw.line(class_name.replace('Test', ''))

        self._tw.line('- [{outcome}] {title}'.format(
            outcome=outcome,
            title=self._format_title(title)
        ))

    def _format_title(self, title):
        title = re.sub(r'^test', '', title)
        return title.replace('_', ' ').strip()
