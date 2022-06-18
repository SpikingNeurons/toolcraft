import numpy as np
import typing as t
import common, symbols

from toolcraft.texipy import Document, Section, Color, SubSection, Fa, \
    FontSize, Positioning, helper, FloatObjAlignment, Scalar
from toolcraft.texipy import table


def compute_simulated_dataset_acc():
    """
    The maximum accuracy for simulated dataset simulated with hw leakage and
    trained with identity labelling

    Also check toy_accuracies.py for more cases ...

    0 39339 39339
    1 38972 312565
    2 38525 1092120
    3 39125 2187142
    4 39072 2735613
    5 39308 2186762
    6 39455 1094727
    7 39042 312835
    8 38897 38897
    3.51735
    """
    _size = 10000000

    _labels = np.random.randint(0, 256, _size, np.uint8)

    _hw_labels = np.vectorize(
        lambda x: bin(x).count("1")
    )(_labels).astype(np.uint8)

    _matched = 0
    for _i in range(9):
        _part_labels = _labels[_hw_labels == _i]
        _part_labels_new = _part_labels.copy()
        np.random.shuffle(_part_labels_new)
        # noinspection PyUnresolvedReferences
        _matched_part = (_part_labels == _part_labels_new).sum()
        _matched += _matched_part
        print(_i, _matched_part, len(_part_labels))

    _acc = _matched / _size

    print(_acc*100.)


def make_table(scale: t.Tuple[float, float] = None):

    # compute_simulated_dataset_acc()

    _table = table.Table(
        type='X',
        scale=scale,
        caption="Results for standard and \\mtovc classifier",
        label="table:results",
        positioning=Positioning(here=True, top=True, special_float_page=True),
        alignment=FloatObjAlignment.centering,
        t_width=Scalar(1, 'textwidth'),
        t_cols_def=table.TableColsDef.from_list(
            items=[
                table.ColumnFmt.insert_before(insert="\\arraybackslash"),
                table.ColumnFmt.para_middle(width=Scalar(0.22, 'textwidth')),
                table.ColumnFmt.insert_before(insert="\\arraybackslash"),
                table.ColumnFmt.para_middle(width=Scalar(0.18, 'textwidth')),
                table.ColumnFmt.insert_before(insert="\\centering\\arraybackslash"),
                table.ColumnFmt.stretched,
                table.ColumnFmt.insert_before(insert="\\centering\\arraybackslash"),
                table.ColumnFmt.stretched,
                table.ColumnFmt.insert_before(insert="\\centering\\arraybackslash"),
                table.ColumnFmt.stretched,
            ],
        )
    )
    # _tikz.show_debug_grid(width=_WIDTH + .01, height=_HEIGHT, step=_STEP)
    # make_fig(_std_traces, _tikz)

    _table.add_toprule()
    _table.add_row(
        table.Row.from_list(
            items=[
                "\\textbf{Dataset}",
                "\\textbf{Model}",
                f"\\boldmath{symbols.glbacc}\\unboldmath~(\\%)",
                f"\\boldmath{symbols.glacc}\\unboldmath~(\\%)",
                f"\\boldmath{symbols.gltgezero}\\unboldmath",
            ],
        )
    )
    _table.add_midrule()
    # _table.add_toprule()
    # ---------------------------------------------------------------- simulated
    _table.add_row(
        table.Row.from_list(
            items=[
                table.MultiRowCell(num_rows=2, value=f"{symbols.gldssim}"),
                "Standard", "0.39", "3.44", "21"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", f"{symbols.mtovc}", "50.0", "100.0", "107"
            ],
        )
    )
    _table.add_cmidrule(n=2, m=5)
    # ---------------------------------------------------------------- simulated-noisy
    _table.add_row(
        table.Row.from_list(
            items=[
                table.MultiRowCell(num_rows=2, value=f"{symbols.gldssimnoisy}"),
                "Standard", "0.39", "3.21", "412"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", f"{symbols.mtovc}", "50.0", "96.78", "272"
            ],
        )
    )
    _table.add_cmidrule(n=2, m=5)
    # ---------------------------------------------------------------- ascad-v1-fk
    _table.add_row(
        table.Row.from_list(
            items=[
                table.MultiRowCell(num_rows=4, value=f"{symbols.gldsascadvonefk}"),
                "Standard \\cite{zaidMethodologyEfficientCNN2020}", "0.39", "---", "191"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", "Standard \\cite{wuChooseYouAutomated2020}", "0.39", "---", "160"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", "Standard", "0.39", "0.71", "190"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", f"{symbols.mtovc}", "50.0", "95.46", "174"
            ],
        )
    )
    _table.add_cmidrule(n=2, m=5)
    # ---------------------------------------------------------------- ascad-v1-vk
    _table.add_row(
        table.Row.from_list(
            items=[
                table.MultiRowCell(num_rows=4, value=f"{symbols.gldsascadvonevk}"),
                "Standard  \\cite{zaidMethodologyEfficientCNN2020}", "0.39", "---", "---"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", "Standard \\cite{wuChooseYouAutomated2020}", "0.39", "---", "3144"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", "Standard", "0.39", "0.64", "3121"
            ],
        )
    )
    _table.add_row(
        table.Row.from_list(
            items=[
                "", f"{symbols.mtovc}", "50.0", "91.36", "2583"
            ],
        )
    )
    _table.add_bottomrule()

    return _table


if __name__ == '__main__':

    # todo: for future papers add these readings for 8-bit dataset and give code with
    #  simulated data so that people can test

    _doc = Document()
    _doc.add_item(make_table())

    _doc.write(save_to_file="try.tex", make_pdf=True)
