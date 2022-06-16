import typing as t
import numpy as np

from toolcraft.texipy import Document, Section, Color, SubSection, Fa
from toolcraft.texipy import tikz
import symbols


class MultiTrunkTrace(t.NamedTuple):
    label: bool
    tid: int
    color: Color
    trace: np.ndarray
    trunk: int
    row: int

    @property
    def node_id(self) -> str:
        return f"mttn{self.trunk:03d}{self.row:02d}"

    @property
    def latex_label(self) -> str:
        return symbols.tracewithid(f"{self.tid:03d}")


class StdTrace(t.NamedTuple):
    label: int
    color: Color
    trace: np.ndarray
    ith: str

    @property
    def node_id(self) -> str:
        return f"stdtn{self.ith}"

    @property
    def latex_label(self) -> str:
        return symbols.tracewithid(self.ith, f"{self.label:03d}")


def get_trace(tid: int) -> np.ndarray:
    return np.random.randint(0, 256, 70, np.uint8)


def std_mt_trunk_traces(
    num_trunks_to_display: int = 4,
    num_traces_per_trunk: int = 8,
    num_traces_for_std: int = 4,
) -> t.Tuple[
    t.List[StdTrace], t.List[MultiTrunkTrace]
]:
    """
    The first return element is for std and other is for mt
    """
    np.random.seed(8573215)

    _possibles_colors = [
        _ for _ in Color if _ not in [_.none, _.white]
    ]
    np.random.shuffle(_possibles_colors)

    _possible_trace_ids_that_will_be_used = \
        [_ for _ in range(num_trunks_to_display-1)] + [255] + list(
            (
                np.random.permutation(
                    256 - num_trunks_to_display) + num_trunks_to_display
            )[:len(_possibles_colors) - num_trunks_to_display]
        )
    np.random.shuffle(_possible_trace_ids_that_will_be_used)

    _trace_colors = {}

    for _i, _tid in enumerate(_possible_trace_ids_that_will_be_used):
        _trace_colors[_tid] = _possibles_colors[_i]

    _mt_labels = np.random.choice(
        a=[True, False], size=num_traces_per_trunk, p=[0.5, 0.5])

    _mt_ret = []
    for _tid in [_ for _ in range(num_trunks_to_display-1)] + [255]:
        for _row in range(num_traces_per_trunk):
            if _mt_labels[_row]:
                _mt_ret.append(
                    MultiTrunkTrace(
                        label=True, tid=_tid, color=_trace_colors[_tid],
                        trace=get_trace(_tid), trunk=_tid, row=_row,
                    )
                )
            else:
                _r_tid = np.random.choice(_possible_trace_ids_that_will_be_used)
                _mt_ret.append(
                    MultiTrunkTrace(
                        label=False, tid=_r_tid, color=_trace_colors[_r_tid],
                        trace=get_trace(_r_tid), trunk=_tid, row=_row,
                    )
                )

    _std_ret = []
    np.random.seed(84654)
    for _index, _tid in enumerate(np.random.choice(
            _possible_trace_ids_that_will_be_used, size=num_traces_for_std)):
        _std_ret.append(
            StdTrace(label=_tid, color=_trace_colors[_tid], trace=get_trace(_tid),
                     ith="M" if _index == (num_traces_for_std-1) else str(_index))
        )

    np.random.seed(None)

    return _std_ret, _mt_ret

#
# _x = std_mt_trunk_traces()
# print(_x)