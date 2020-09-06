from collections import Counter

import pytest

from pytest_testdox import constants


class TestReport:

    @pytest.fixture
    def testdir(self, testdir):
        testdir.makeconftest("""
            pytest_plugins = 'pytest_testdox.plugin'
        """)
        return testdir

    def test_should_print_a_green_passing_test(self, testdir):
        testdir.makepyfile("""
            def test_a_feature_is_working():
                assert True
        """)

        result = testdir.runpytest('--force-testdox')

        expected = '\033[92m ✓ a feature is working\033[0m'
        assert expected in result.stdout.str()

    def test_should_print_a_red_failing_test(self, testdir):
        testdir.makepyfile("""
            def test_a_failed_test_of_a_feature():
                assert False
        """)

        result = testdir.runpytest('--force-testdox')
        expected = '\033[91m ✗ a failed test of a feature\033[0m'

        assert expected in result.stdout.str()

    def test_should_print_a_yellow_skipped_test(self, testdir):
        testdir.makepyfile("""
            import pytest

            @pytest.mark.skip
            def test_a_skipped_test():
                pass
        """)

        result = testdir.runpytest('--force-testdox')
        expected = '\033[93m » a skipped test\033[0m'

        assert expected in result.stdout.str()

    def test_should_not_print_colors_when_disabled_by_parameter(self, testdir):
        testdir.makepyfile("""
            def test_a_feature_is_working():
                assert True
        """)
        result = testdir.runpytest(
            '--color=no',
            '--force-testdox'
        )

        assert '\033[92m' not in result.stdout.str()

    def test_should_output_plaintext_using_a_config_option(self, testdir):
        testdir.makeini("""
            [pytest]
            testdox_format=plaintext
        """)
        testdir.makepyfile("""
            def test_a_feature_is_working():
                assert True
        """)
        result = testdir.runpytest('--force-testdox')

        expected = '\033[92m [x] a feature is working\033[0m'
        assert expected in result.stdout.str()

    def test_should_print_the_test_class_name(self, testdir):
        testdir.makepyfile("""
            class TestFoo:
                def test_foo(self):
                    pass

            class TestBar:
                def test_bar(self):
                    pass
        """)
        result = testdir.runpytest('--force-testdox')

        lines = result.stdout.get_lines_after('Foo')
        assert '✓ foo' in lines[0]

        lines = result.stdout.get_lines_after('Bar')
        assert '✓ bar' in lines[0]

    def test_should_print_the_module_name_of_a_test_without_class(
        self,
        testdir
    ):
        testdir.makefile('.py', test_module_name="""
            def test_a_failed_test_of_a_feature():
                assert False
        """)

        result = testdir.runpytest('--force-testdox')
        result.stdout.fnmatch_lines(['module name'])

    def test_should_print_test_summary(self, testdir):
        testdir.makefile('.py', test_module_name="""
            def test_a_passing_test():
                assert True
        """)

        result = testdir.runpytest('--force-testdox')
        assert '1 passed' in result.stdout.str()

    def test_should_use_python_patterns_configuration(self, testdir):
        testdir.makeini("""
            [pytest]
            python_classes=Describe*
            python_files=*spec.py
            python_functions=it*
        """)
        testdir.makefile('.py', module_spec="""
            class DescribeTest:
                def it_runs(self):
                    pass
        """)

        result = testdir.runpytest('--force-testdox')

        lines = result.stdout.get_lines_after('Test')
        assert '✓ runs' in lines[0]

    def test_should_override_test_titles_with_title_mark(
        self,
        testdir
    ):
        testdir.makefile('.py', test_module_name="""
            import pytest

            @pytest.mark.{}('''
                My Title
                My precious title
            ''')
            def test_a_passing_test():
                assert True
        """.format(
            constants.TITLE_MARK
        ))

        result = testdir.runpytest('--force-testdox')

        assert 'My Title\n   My precious title' in result.stdout.str()

    def test_should_override_class_names_with_class_name_mark(
        self,
        testdir
    ):
        testdir.makefile('.py', test_module_name="""
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
        ))

        result = testdir.runpytest('--force-testdox')

        assert 'My Class\nMy precious class' in result.stdout.str()

    def test_should_override_test_titles_with_title_mark_parametrize(
        self,
        testdir
    ):
        testdir.makefile('.py', test_module_name="""
            import pytest

            @pytest.mark.parametrize('par', ['param1', 'param2'])
            @pytest.mark.{}('should pass with parameters')
            def test_a_passing_test(par):
                assert True
        """.format(
            constants.TITLE_MARK
        ))

        result = testdir.runpytest('--force-testdox')

        assert 'should pass with parameters[param1]' in result.stdout.str()
        assert 'should pass with parameters[param2]' in result.stdout.str()

    def test_decorator_order_should_not_affect_parametrize(
        self,
        testdir
    ):
        testdir.makefile('.py', test_module_name="""
            import pytest

            @pytest.mark.{}('should pass with parameters')
            @pytest.mark.parametrize('par', ['param1', 'param2'])
            def test_a_passing_test(par):
                assert True
        """.format(
            constants.TITLE_MARK
        ))

        result = testdir.runpytest('--force-testdox')

        assert 'should pass with parameters[param1]' in result.stdout.str()
        assert 'should pass with parameters[param2]' in result.stdout.str()

    def test_should_not_enable_plugin_when_test_run_out_of_tty(self, testdir):
        testdir.makepyfile("""
            def test_a_feature_is_working():
                assert True
        """)

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
            """
        )

        result = testdir.runpytest('--force-testdox')
        word_count = Counter(result.stdout.lines)

        assert word_count['Foo'] == 2
