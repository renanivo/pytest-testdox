# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_testdox import formatters


class TestFormatOutcome(object):

    def test_should_return_x_when_passed(self):
        assert formatters.format_outcome('passed') == 'x'

    def test_should_return_a_space_when_failed(self):
        assert formatters.format_outcome('failed') == ' '


class TestFormatTitle(object):

    def test_should_replace_underscores_with_spaces(self):
        assert formatters.format_title('a_test_name') == 'a test name'

    def test_should_remove_test_prefix(self):
        assert formatters.format_title('test_a_thing') == 'a thing'
        assert formatters.format_title('a_thing_test') == 'a thing test'


class TestFormatClassName(object):

    def test_should_add_spaces_before_upercased_letters(self):
        result = formatters.format_class_name('AThingBuilder')
        assert result == 'A Thing Builder'

    def test_should_remove_test_prefix(self):
        assert formatters.format_class_name('TestAThing') == 'A Thing'
        assert formatters.format_class_name('AThingTest') == 'A Thing Test'


class TestFormatModuleName(object):

    def test_should_remove_py_file_suffix(self):
        assert formatters.format_module_name('pymodule.py') == 'pymodule'

    def test_should_replace_underscores_with_spaces(self):
        assert formatters.format_module_name('a_test_name') == 'a test name'

    def test_should_remove_test_prefix(self):
        assert formatters.format_module_name('test_a_thing.py') == 'a thing'
        assert formatters.format_module_name('a_test.py') == 'a test'

    def test_should_replace_slashes_with_dots(self):
        assert formatters.format_module_name('sub/module.py') == 'sub.module'
