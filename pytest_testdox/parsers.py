# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from collections import namedtuple

from . import formatters

Node = namedtuple('Node', 'title class_name module_name')


def parse_node(nodeid):
    node_parts = nodeid.split('::')
    title = formatters.format_title(node_parts[-1])
    module_name = formatters.format_module_name(
        re.sub('.py$', '', node_parts[0]).replace('/', '.')
    )

    class_name = node_parts[-2]
    if '()' not in class_name:
        class_name = None
    else:
        class_name = formatters.format_class_name(node_parts[-3])

    return Node(title, class_name, module_name)
