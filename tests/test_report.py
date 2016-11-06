# -*- coding: utf-8 -*-


class TestReport(object):

    def test_prints_a_passing_test(self, testdir):
        testdir.makepyfile("""
            def test_a_feature_is_working():
                assert True
        """)

        result = testdir.runpytest('--testdox')
        result.stdout.fnmatch_lines('- [x] a feature is working')

    def test_prints_a_failing_test(self, testdir):
        testdir.makepyfile("""
            def test_a_failed_test_of_a_feature():
                assert False
        """)

        result = testdir.runpytest('--testdox')
        result.stdout.fnmatch_lines('- [ ] a failed test of a feature')

    def test_prints_the_test_class_name(self, testdir):
        testdir.makepyfile("""
            class TestFoo(object):
                def test_foo(self):
                    pass

            class TestBar(object):
                def test_bar(self):
                    pass
        """)
        result = testdir.runpytest('--testdox')

        lines = result.stdout.get_lines_after('Foo')
        assert '- [x] foo' in lines[0]

        lines = result.stdout.get_lines_after('Bar')
        assert '- [x] bar' in lines[0]

    def test_prints_the_module_name(self, testdir):
        testdir.makefile('.py', test_module_name="""
            def test_a_failed_test_of_a_feature():
                assert False
        """)

        result = testdir.runpytest('--testdox')
        result.stdout.fnmatch_lines('module name')
