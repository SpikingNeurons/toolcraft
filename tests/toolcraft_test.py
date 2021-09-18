#!/usr/bin/env python
"""Tests for `toolcraft` package."""
# pylint: disable=redefined-outer-name
import pytest
from typer.testing import CliRunner

from toolcraft import tools


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
    ...


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(tools.main)
    assert result.exit_code == 0
    assert "toolcraft.tools.main" in result.output
    # noinspection PyTypeChecker
    help_result = runner.invoke(tools.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
