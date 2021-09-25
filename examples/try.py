import dataclasses
import datetime
import time
import typing as t

import pytest
from typer.testing import CliRunner

from toolcraft import rules, tools

runner = CliRunner()
result = runner.invoke(tools.APP, ["--help"])
print(">>>>>>>>>>>>>", result.output, "<<<<<<<<<<<<<<<<<<<<<<<<<")
