from typing import TextIO

try:
    from pytest import Config, TestReport  # type: ignore
except ImportError:  # For pytest < 7.0.0
    from _pytest.config import Config
    from _pytest.reports import TestReport

from _pytest.terminal import TerminalReporter

from pytest_testdox import data_structures, wrappers


class TestdoxTerminalReporter(TerminalReporter):  # type: ignore
    def __init__(self, config: Config, file: TextIO | None = None) -> None:
        super().__init__(config, file)
        self._last_header_id: str | None = None
        self._last_group_id: str | None = None
        self.group_params = config.getoption('testdox_group_params')
        if self.group_params is None:
            self.group_params = config.getini('testdox_group_params')
        self.pattern_config = data_structures.PatternConfig(
            files=self.config.getini('python_files'),
            functions=self.config.getini('python_functions'),
            classes=self.config.getini('python_classes'),
        )
        self.result_wrappers: list[type] = []

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

        group_id = (
            getattr(report, 'testdox_group_id', None)
            if self.group_params
            else None
        )
        if group_id is not None:
            node = data_structures.Node.parse(
                group_id,
                self.pattern_config,
                title=getattr(report, 'testdox_title', None),
                class_name=getattr(report, 'testdox_class_name', None),
            )
            group_title = str(node)
            node.title = report.testdox_param_id
            result = data_structures.Result(report.outcome, node)
        else:
            result = data_structures.Result.create(report, self.pattern_config)

        for wrapper in self.result_wrappers:
            result = wrapper(result)

        if result.header_id != self._last_header_id:
            self._last_header_id = result.header_id
            self._tw.sep(' ')
            self._tw.line(result.header)

        if group_id is not None and group_id != self._last_group_id:
            self._tw.line('   ' + group_title.replace('\n', '\n   '))
        self._last_group_id = group_id

        self._tw.line(('   ' if group_id is not None else '') + str(result))

    def pytest_runtest_logstart(
        self, nodeid: str, location: tuple[str, int | None, str]
    ) -> None:
        # Ensure that the path is printed before the
        # 1st test of a module starts running.
        self.write_fspath_result(nodeid, '')

        # To support Pytest < 6.0.0
        if hasattr(self, 'flush'):
            self.flush()
