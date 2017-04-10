# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from pytest_testdox import formatters, parsers


class TestParseNodeId(object):

    @pytest.fixture
    def pattern_config(self):
        return parsers.PatternConfig(
            files=['test_*.py'],
            functions=['test*'],
            classes=['Test*']
        )

    def test_should_return_a_node_instance(self, pattern_config):
        nodeid = 'tests/test_module.py::test_title'
        node = parsers.parse_node(nodeid, pattern_config)

        assert isinstance(node, parsers.Node)

    def test_should_parse_node_id_attributes(self, pattern_config):
        nodeid = 'tests/test_module.py::test_title'
        node = parsers.parse_node(nodeid, pattern_config)

        assert node.title == formatters.format_title('test_title',
                                                     pattern_config.functions)
        assert node.module_name == (
            formatters.format_module_name('tests/test_module.py',
                                          pattern_config.files)
        )

    @pytest.mark.parametrize('nodeid,class_name', (
        ('tests/test_module.py::test_title', None),
        (
            'tests/test_module.py::TestClassName::()::test_title',
            formatters.format_class_name('TestClassName', ['Test*'])
        )
    ))
    def test_should_parse_class_name(self, pattern_config, nodeid, class_name):
        node = parsers.parse_node(nodeid, pattern_config)

        assert node.class_name == class_name
