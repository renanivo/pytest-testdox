# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

import six

from . import formatters


PatternConfig = namedtuple('PatternConfig', 'files functions classes')


@six.python_2_unicode_compatible
class Node(object):

    def __init__(self, title, class_name, module_name):
        self.title = title
        self.class_name = class_name
        self.module_name = module_name

    def __str__(self):
        return self.title

    def __repr__(self):
        items = (
            '{}={!r}'.format(key, getattr(self, key))
            for key in ('title', 'class_name', 'module_name')
        )
        return '{}({})'.format(
            type(self).__name__,
            items
        )

    @classmethod
    def parse(cls, nodeid, pattern_config):
        node_parts = nodeid.split('::')
        title = formatters.format_title(
            node_parts[-1],
            pattern_config.functions
        )
        module_name = formatters.format_module_name(
            node_parts[0],
            pattern_config.files
        )

        class_name = node_parts[-2]
        if '()' not in class_name:
            class_name = None
        else:
            class_name = formatters.format_class_name(
                node_parts[-3],
                pattern_config.classes
            )

        return cls(title=title, class_name=class_name, module_name=module_name)


@six.python_2_unicode_compatible
class Result(object):

    def __init__(self, outcome, node):
        self.outcome = outcome
        self.node = node

    def __str__(self):
        line = '- [{outcome}] {node}'.format(
            outcome=formatters.format_outcome(self.outcome),
            node=self.node
        )
        return formatters.colored(line, self.outcome)

    @property
    def header(self):
        return self.node.class_name or self.node.module_name

    @classmethod
    def create(cls, report, pattern_config):
        from . import parsers
        node = parsers.parse_node(report.nodeid, pattern_config)

        return cls(report.outcome, node)
