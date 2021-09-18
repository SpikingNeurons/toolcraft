#!/usr/bin/env python
"""Tests for `toolcraft` package."""
# pylint: disable=redefined-outer-name
import pytest
from toolcraft import rules
from toolcraft import tools
from typer.testing import CliRunner


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
    result = runner.invoke(tools.APP, ["--help"])
    assert result.exit_code == 0
    assert "toolcraft" in result.output


def test_toolcraft_rules():
    rules.main()
