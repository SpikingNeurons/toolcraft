import dataclasses
import datetime
import time
import typing as t
import pytest
from toolcraft import rules
from toolcraft import tools
from typer.testing import CliRunner
from toolcraft import tools

runner = CliRunner()
result = runner.invoke(tools.APP, ["--help"])
print(">>>>>>>>>>>>>", result.output, "<<<<<<<<<<<<<<<<<<<<<<<<<")
