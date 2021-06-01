import os

import pytest

from pytest_testdox import formatters


class TestFormatTitle:

    @pytest.fixture
    def patterns(self):
        return ['test*']

    def test_should_replace_underscores_with_spaces(self, patterns):
        assert formatters.format_title('a_test_name', patterns) == (
            'a test name'
        )

    def test_should_remove_test_pattern(self, patterns):
        assert formatters.format_title('test_a_thing', patterns) == 'a thing'
        assert formatters.format_title('a_thing_test', patterns) == (
            'a thing test'
        )


class TestFormatClassName:

    @pytest.fixture
    def patterns(self):
        return ['Test*']

    def test_should_add_spaces_before_upercased_letters(self, patterns):
        formatted = formatters.format_class_name('AThingBuilder', patterns)
        assert formatted == 'A Thing Builder'

    def test_should_remove_test_pattern(self, patterns):
        assert formatters.format_class_name('TestAThing', patterns) == (
            'A Thing'
        )
        assert formatters.format_class_name('AThingTest', patterns) == (
            'A Thing Test'
        )

    @pytest.mark.parametrize('class_name,expected', (
        ('SimpleHTTPServer', 'Simple HTTP Server'),
        ('MyAPI', 'My API'),
    ))
    def test_should_not_split_letters_in_an_abbreviation(
        self,
        class_name,
        expected,
        patterns
    ):
        formatted = formatters.format_class_name(class_name, patterns)
        assert formatted == expected


class TestFormatModuleName:

    @pytest.fixture
    def patterns(self):
        return ['test*.py']

    def test_should_remove_py_file_pattern(self, patterns):
        assert formatters.format_module_name('pymodule.py', patterns) == (
            'pymodule'
        )

    def test_should_replace_underscores_with_spaces(self, patterns):
        assert formatters.format_module_name('a_test_name', patterns) == (
            'a test name'
        )

    def test_should_remove_test_pattern(self, patterns):
        assert formatters.format_module_name('test_a_thing.py', patterns) == (
            'a thing'
        )
        assert formatters.format_module_name('a_test.py', patterns) == 'a test'

    def test_should_remove_folders_from_the_name(self, patterns):
        formatted = formatters.format_module_name(
            'tests/sub/test_module.py',
            patterns
        )

        assert formatted == 'module'

    def test_should_remove_infix_glob_patterns(self):
        formatted = formatters.format_module_name(
            'test_module.py',
            ['test_*.py']
        )

        assert formatted == 'module'


class TestTrimMultiLineText:

    def test_should_strip_spaces_from_begin_and_end(self):
        assert formatters.trim_multi_line_text('  works   ') == 'works'

    def test_should_srip_spaces_from_multiple_lines(self):
        assert formatters.trim_multi_line_text('''
            works when used in very specific
            conditions of temperature and pressure
        ''') == (
            'works when used in very specific\n'
            'conditions of temperature and pressure'
        )


class TestPadTextToCharacters:

    def test_should_not_pad_single_line_text(self):
        assert formatters.pad_text_to_characters_length(
            'some text', '>>>'
        ) == (
            'some text'
        )

    def test_should_pad_the_following_lines_to_the_width_of_given_characters(
        self
    ):
        text = (
            'first line{0}'
            'second line{0}'
            'third line{0}'
            'fourth line'
        ).format(
            os.linesep
        )
        assert formatters.pad_text_to_characters_length(text, '>>>') == (
            'first line{0}'
            '   second line{0}'
            '   third line{0}'
            '   fourth line'.format(
                os.linesep
            )
        )

    def test_should_remove_empty_lines(self):
        text = (
            'first line{0}'
            '{0}'
            'second line{0}'
            '{0}'
            '{0}'
            'third line'
        ).format(
            os.linesep
        )
        assert formatters.pad_text_to_characters_length(text, '>>>') == (
            'first line{0}'
            '   second line{0}'
            '   third line'.format(
                os.linesep
            )
        )


class TestIncludeParametrized:

    def test_should_return_title_when_no_parameters_are_found(self):
        assert formatters.include_parametrized(
            title='Should return value',
            original_title='test_should_return_value'
        ) == 'Should return value'

    def test_should_return_parameters_in_title(self):
        assert formatters.include_parametrized(
            title='A title',
            original_title='test_should_return_value[params]'
        ) == 'A title[params]'

    def test_should_return_parameters_containing_brackets(self):
        assert formatters.include_parametrized(
            title='A title',
            original_title='test_should_return_value[[[[params]]]]'
        ) == 'A title[[[[params]]]]'
