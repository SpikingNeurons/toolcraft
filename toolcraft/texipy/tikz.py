"""
Supporting tutorial: https://www.overleaf.com/learn/latex/TikZ_package
"""

import dataclasses
import typing as t

from .__base__ import LaTeX


@dataclasses.dataclass
class TikZ(LaTeX):
    ...