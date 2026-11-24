from collections import Counter

import pytest

from pytest_testdox import constants


class TestReport:
    def test_should_print_a_green_passing_test(self, testdir):
        testdir.makepyfile(
            """
            def test_a_feature_is_working():
                assert True
            """
        )

        result = testdir.runpytest('--force-testdox')

        expected = '\033[92m ✓ a feature is working\033[0m'
        assert expected in result.stdout.str()

    def test_should_print_a_red_failing_test(self, testdir):
        testdir.makepyfile(
            """
            def test_a_failed_test_of_a_feature():
                assert False
            """
        )

        result = testdir.runpytest('--force-testdox')
        expected = '\033[91m ✗ a failed test of a feature\033[0m'

        assert expected in result.stdout.str()

    def test_should_print_a_yellow_skipped_test(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.skip
            def test_a_skipped_test():
                pass
            """
        )

        result = testdir.runpytest('--force-testdox')
        expected = '\033[93m » a skipped test\033[0m'

        assert expected in result.stdout.str()

    def test_should_not_print_colors_when_disabled_by_parameter(self, testdir):
        testdir.makepyfile(
            """
            def test_a_feature_is_working():
                assert True
            """
        )
        result = testdir.runpytest('--color=no', '--force-testdox')

        assert '\033[92m' not in result.stdout.str()

    def test_should_output_plaintext_using_a_config_option(self, testdir):
        testdir.makeini(
            """
            [pytest]
            testdox_format=plaintext
            """
        )
        testdir.makepyfile(
            """
            def test_a_feature_is_working():
                assert True
            """
        )
        result = testdir.runpytest('--force-testdox')

        expected = '\033[92m [x] a feature is working\033[0m'
        assert expected in result.stdout.str()

    def test_should_print_the_test_class_name(self, testdir):
        testdir.makepyfile(
            """
            class TestFoo:
                def test_foo(self):
                    pass

            class TestBar:
                def test_bar(self):
                    pass
            """
        )
        result = testdir.runpytest('--force-testdox')

        lines = result.stdout.get_lines_after('Foo')
        assert '✓ foo' in lines[0]

        lines = result.stdout.get_lines_after('Bar')
        assert '✓ bar' in lines[0]

    def test_should_print_the_module_name_of_a_test_without_class(
        self, testdir
    ):
        testdir.makefile(
            '.py',
            test_module_name="""
            def test_a_failed_test_of_a_feature():
                assert False
            """,
        )

        result = testdir.runpytest('--force-testdox')
        result.stdout.fnmatch_lines(['module name'])

    def test_should_print_test_summary(self, testdir):
        testdir.makefile(
            '.py',
            test_module_name="""
            def test_a_passing_test():
                assert True
            """,
        )

        result = testdir.runpytest('--force-testdox')
        assert '1 passed' in result.stdout.str()

    def test_should_use_python_patterns_configuration(self, testdir):
        testdir.makeini(
            """
            [pytest]
            python_classes=Describe*
            python_files=*spec.py
            python_functions=it*
            """
        )
        testdir.makefile(
            '.py',
            module_spec="""
            class DescribeTest:
                def it_runs(self):
                    pass
            """,
        )

        result = testdir.runpytest('--force-testdox')

        lines = result.stdout.get_lines_after('Test')
        assert '✓ runs' in lines[0]

    def test_should_override_test_titles_with_title_mark(self, testdir):
        testdir.makefile(
            '.py',
            test_module_name="""
            import pytest

            @pytest.mark.{}('''
                My Title
                My precious title
            ''')
            def test_a_passing_test():
                assert True
            """.format(
                constants.TITLE_MARK
            ),
        )

        result = testdir.runpytest('--force-testdox')

        assert 'My Title\n   My precious title' in result.stdout.str()

    def test_should_override_class_names_with_class_name_mark(self, testdir):
        testdir.makefile(
            '.py',
            test_module_name="""
            import pytest

            @pytest.mark.{}('''
                My Class
                My precious class
            ''')
            class TestClass:

                def test_foo(self):
                    pass
            """.format(
                constants.CLASS_NAME_MARK
            ),
        )

        result = testdir.runpytest('--force-testdox')

        assert 'My Class\nMy precious class' in result.stdout.str()

    def test_should_override_test_titles_with_title_mark_parametrize(
        self, testdir
    ):
        testdir.makefile(
            '.py',
            test_module_name="""
            import pytest

            @pytest.mark.parametrize('par', ['param1', 'param2'])
            @pytest.mark.{}('should pass with parameters')
            def test_a_passing_test(par):
                assert True
            """.format(
                constants.TITLE_MARK
            ),
        )

        result = testdir.runpytest('--force-testdox', '--color=no')

        result.assert_outcomes(passed=2)
        assert '   should pass with parameters' in result.stdout.lines
        assert '    ✓ param1' in result.stdout.lines
        assert '    ✓ param2' in result.stdout.lines

    def test_decorator_order_should_not_affect_parametrize(self, testdir):
        testdir.makefile(
            '.py',
            test_module_name="""
            import pytest

            @pytest.mark.{}('should pass with parameters')
            @pytest.mark.parametrize('par', ['param1', 'param2'])
            def test_a_passing_test(par):
                assert True
            """.format(
                constants.TITLE_MARK
            ),
        )

        result = testdir.runpytest('--force-testdox', '--color=no')

        result.assert_outcomes(passed=2)
        assert '   should pass with parameters' in result.stdout.lines
        assert '    ✓ param1' in result.stdout.lines
        assert '    ✓ param2' in result.stdout.lines

    @pytest.mark.parametrize(
        'ini_value, option',
        [
            (None, None),
            ('true', None),
            ('false', '--testdox-group-params'),
        ],
    )
    @pytest.mark.parametrize('output_format', ['utf8', 'plaintext'])
    def test_should_group_parametrized_results(
        self, testdir, ini_value, option, output_format
    ):
        ini = '[pytest]\ntestdox_format = {}'.format(output_format)
        if ini_value is not None:
            ini += '\ntestdox_group_params = ' + ini_value
        testdir.makeini(ini)
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.parametrize('value', [
                pytest.param(1, id='blue_sky[light]::day'),
                pytest.param(0, id='failure'),
                pytest.param(2, id='skip', marks=pytest.mark.skip),
            ])
            @pytest.mark.it('works with parameters')
            def test_values(value):
                assert value

            def test_regular():
                pass
            """
        )
        args = ['--force-testdox', '--color=no']
        if option:
            args.append(option)
        result = testdir.runpytest(*args)

        result.assert_outcomes(passed=2, failed=1, skipped=1)
        symbols = (
            ('✓', '✗', '»')
            if output_format == 'utf8'
            else ('[x]', '[ ]', '>>>')
        )
        expected = [
            '   works with parameters',
            '    {} blue_sky[light]::day'.format(symbols[0]),
            '    {} failure'.format(symbols[1]),
            '    {} skip'.format(symbols[2]),
            ' {} regular'.format(symbols[0]),
        ]
        lines = result.stdout.lines
        start = lines.index(expected[0])
        assert lines[start : start + len(expected)] == expected
        assert lines.count(expected[0]) == 1

    @pytest.mark.parametrize(
        'ini_value, option',
        [
            (None, '--no-testdox-group-params'),
            ('false', None),
            ('true', '--no-testdox-group-params'),
        ],
    )
    def test_should_show_full_test_titles_when_grouping_is_disabled(
        self, testdir, ini_value, option
    ):
        if ini_value is not None:
            testdir.makeini('[pytest]\ntestdox_group_params = ' + ini_value)
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.parametrize('value', ['blue', 'green'])
            def test_colors(value):
                pass
            """
        )
        args = ['--force-testdox', '--color=no']
        if option:
            args.append(option)
        result = testdir.runpytest(*args)

        result.assert_outcomes(passed=2)
        assert ' ✓ colors[blue]' in result.stdout.lines
        assert ' ✓ colors[green]' in result.stdout.lines
        assert '   colors' not in result.stdout.lines

    def test_should_group_parametrized_fixtures_with_colors(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.fixture(params=['blue_sky', 'green_field'])
            def color(request):
                return request.param

            def test_colors(color):
                pass
            """
        )
        result = testdir.runpytest('--force-testdox', '--testdox-group-params')

        result.assert_outcomes(passed=2)
        lines = result.stdout.lines
        start = lines.index('   colors')
        assert lines[start + 1 : start + 3] == [
            '   \033[92m ✓ blue_sky\033[0m',
            '   \033[92m ✓ green_field\033[0m',
        ]

    def test_should_keep_groups_separate_for_tests_with_the_same_title(
        self, testdir
    ):
        source = """
            import pytest

            class TestColors:
                @pytest.mark.it('same title')
                @pytest.mark.parametrize('value', ['blue', 'green'])
                def test_first(self, value):
                    pass

                @pytest.mark.it('same title')
                @pytest.mark.parametrize('value', ['blue', 'green'])
                def test_second(self, value):
                    pass
        """
        testdir.makepyfile(test_first=source, test_second=source)
        result = testdir.runpytest(
            '--force-testdox', '--testdox-group-params', '--color=no'
        )

        result.assert_outcomes(passed=8)
        lines = result.stdout.lines
        assert lines.count('   same title') == 4
        assert lines.count('    ✓ blue') == 4
        assert lines.count('    ✓ green') == 4

    def test_should_not_enable_plugin_when_test_run_out_of_tty(self, testdir):
        testdir.makepyfile(
            """
            def test_a_feature_is_working():
                assert True
            """
        )

        result = testdir.runpytest('--testdox')

        expected_testdox_output = '\033[92m ✓ a feature is working\033[0m'

        assert expected_testdox_output not in result.stdout.str()

    def test_should_not_aggregate_tests_under_same_class_in_different_modules(
        self, testdir
    ):
        testdir.makepyfile(
            test_first="""
            class TestFoo(object):
                def test_a_feature_is_working(self):
                    assert True
            """,
            test_second="""
            class TestFoo(object):
                def test_a_feature_is_working_in_another_module(self):
                    assert True
            """,
        )

        result = testdir.runpytest('--force-testdox')
        word_count = Counter(result.stdout.lines)

        assert word_count['Foo'] == 2

    def test_verbose_mode_should_not_affect_the_filename_output(self, testdir):
        file = testdir.makepyfile(
            """
            def test_foo():
                assert True

            def test_bar():
                assert True
            """
        )

        result = testdir.runpytest('--verbose', '--force-testdox')

        result.stdout.re_match_lines(r'^' + file.basename + r'\s+$')
