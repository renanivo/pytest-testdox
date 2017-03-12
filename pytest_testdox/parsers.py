# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from . import formatters

Node = namedtuple('Node', 'title class_name module_name')
PatternConfig = namedtuple('PatternConfig', 'files functions classes')


def parse_node(nodeid, pattern_config):
    node_parts = nodeid.split('::')
    title = formatters.format_title(node_parts[-1], pattern_config.functions)
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

    return Node(title, class_name, module_name)
