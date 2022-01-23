import pathlib
import dataclasses

from toolcraft import marshalling as m
from toolcraft.tools import dapr


@dataclasses.dataclass(frozen=True)
class Test(m.HashableClass):
    a: int


if __name__ == '__main__':
    dapr.launch_dapr_app()
