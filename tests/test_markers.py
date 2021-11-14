import pytest


class TestMarkers:
    @pytest.fixture
    def testdir(self, testdir):
        testdir.makeconftest(
            """
            pytest_plugins = 'pytest_testdox.plugin'
        """
        )
        return testdir

    def test_should_not_raise_warning_without_plugin_call(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.it('Should not raise warning')
            def test_with_plugin_mark():
                assert True
        """
        )

        result = testdir.runpytest()

        unknown_mark_warning = 'PytestUnknownMarkWarning'

        assert unknown_mark_warning not in result.stdout.str()
        assert '1 passed' in result.stdout.str()
