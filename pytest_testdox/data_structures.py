from __future__ import annotations

from dataclasses import dataclass
from typing import List, NamedTuple

from _pytest.reports import TestReport

from pytest_testdox import formatters


class PatternConfig(NamedTuple):
    files: List[str]
    functions: List[str]
    classes: List[str]


@dataclass
class Node:
    module_name: str
    title: str | None
    class_name: str | None

    def __str__(self):
        return self.title

    @classmethod
    def parse(
        cls,
        nodeid: str,
        pattern_config: PatternConfig,
        title: str | None = None,
        class_name: str | None = None,
    ):
        node_parts = nodeid.split('::')

        if title:
            title = formatters.include_parametrized(
                formatters.trim_multi_line_text(title), node_parts[-1]
            )
        else:
            title = formatters.format_title(
                node_parts[-1], pattern_config.functions
            )

        module_name = formatters.format_module_name(
            node_parts[0], pattern_config.files
        )

        if class_name:
            class_name = formatters.trim_multi_line_text(class_name)
        else:
            if '()' in node_parts[-2]:
                class_name = formatters.format_class_name(
                    node_parts[-3], pattern_config.classes
                )
            elif len(node_parts) > 2:
                class_name = formatters.format_class_name(
                    node_parts[-2], pattern_config.classes
                )

        return cls(title=title, class_name=class_name, module_name=module_name)


@dataclass(frozen=True)
class Result:
    outcome: str
    node: Node

    _OUTCOME_REPRESENTATION = {
        'passed': ' [x] ',
        'failed': ' [ ] ',
        'skipped': ' >>> ',
    }
    _default_outcome_representation = '>>>'

    def __str__(self) -> str:
        representation = self._OUTCOME_REPRESENTATION.get(
            self.outcome, self._default_outcome_representation
        )

        return formatters.format_result_str(
            outcome=representation, node_str=str(self.node)
        )

    @property
    def header(self) -> str:
        return self.node.class_name or self.node.module_name  # type: ignore

    @property
    def header_id(self) -> str:
        """
        Return the same value when the result should be aggregated under the
        same class or module (this is not guaranteed in "header" property,
        which should be used when displaying to the user)
        """
        return self.node.module_name + (self.node.class_name or '')

    @classmethod
    def create(
        cls, report: TestReport, pattern_config: PatternConfig
    ) -> Result:
        title = getattr(report, 'testdox_title', None)
        class_name = getattr(report, 'testdox_class_name', None)

        node = Node.parse(
            nodeid=report.nodeid,
            pattern_config=pattern_config,
            title=title,
            class_name=class_name,
        )
        return cls(report.outcome, node)
