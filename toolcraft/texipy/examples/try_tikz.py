"""
We do this tutorial in texipy
https://www.overleaf.com/learn/latex/TikZ_package

Examples: https://jeltef.github.io/PyLaTeX/current/examples.html
Overleaf: https://www.overleaf.com/project/61e156e866cd5fcf894967ca
"""
import numpy as np
import typing as t

from toolcraft.texipy import Document, Section, Color, SubSection, Fa, \
    FontSize, Positioning, FloatObjAlignment
from toolcraft.texipy import tikz
from toolcraft import error as e
import common
import symbols

_WIDTH = tikz.Scalar(1, 'textwidth')
_HEIGHT = _WIDTH * 0.8
_STEP = tikz.Scalar(0.1, 'cm')


def make_label_nodes(_tikz: tikz.TikZ) -> t.Dict[str, t.Dict[int, tikz.Node]]:
    _path = tikz.Path()

    _path.move_to(tikz.Point2D(_WIDTH * 0.5, _HEIGHT * 0.05))
    _hw_hidden_node = tikz.Node(id="hw")
    _path.add_node(_hw_hidden_node)
    _path.move_to(tikz.Point2D(_WIDTH * 0.95, _HEIGHT * 0.5))
    _lsb_hidden_node = tikz.Node(id="lsb")
    _path.add_node(_lsb_hidden_node)
    _path.move_to(tikz.Point2D(_WIDTH * 0.5, _HEIGHT * 0.95))
    _id_hidden_node = tikz.Node(id="id")
    _path.add_node(_id_hidden_node)
    _path.move_to(tikz.Point2D(_WIDTH * 0.05, _HEIGHT * 0.5))
    _msb_hidden_node = tikz.Node(id="msb")
    _path.add_node(_msb_hidden_node)

    # make nodes
    _ret = {}

    # ----------------------------------------- hw
    _ret['hw'] = {}
    _path.move_to(_hw_hidden_node.center)
    _ret['hw'][1] = tikz.Node(
        id="hw01", text_to_display=symbols.labelwithlk('hw', '1')
    )
    _path.add_node(_ret['hw'][1])
    _ret['hw'][0] = tikz.Node(
        id="hw00",
        text_to_display=symbols.labelwithlk('hw', '0'),
        anchor=tikz.Anchor.left(offset=_WIDTH * 0.15),
    )
    _path.add_node(_ret['hw'][0])
    _ret['hw'][2] = tikz.Node(
        id="hw02",
        text_to_display=symbols.labelwithlk('hw', '2'),
        anchor=tikz.Anchor.right(offset=_WIDTH * 0.15),
    )
    _path.add_node(_ret['hw'][2])

    # ----------------------------------------- lsb
    _ret['lsb'] = {}
    _path.move_to(_lsb_hidden_node.center)
    _ret['lsb'][1] = tikz.Node(
        id="lsb01",
        text_to_display=symbols.labelwithlk('lsb', '1'),
        anchor=tikz.Anchor.below(offset=_WIDTH * 0.1),
    )
    _path.add_node(_ret['lsb'][1])
    _ret['lsb'][0] = tikz.Node(
        id="lsb00",
        text_to_display=symbols.labelwithlk('lsb', '0'),
        anchor=tikz.Anchor.above(offset=_WIDTH * 0.1),
    )
    _path.add_node(_ret['lsb'][0])

    # ----------------------------------------- id
    _ret['id'] = {}
    _path.move_to(_id_hidden_node.center)
    _ret['id'][0] = tikz.Node(
        id="id00",
        text_to_display=symbols.labelwithlk('id', '0'),
        anchor=tikz.Anchor.left(offset=_WIDTH * 0.2),
    )
    _path.add_node(_ret['id'][0])
    _path.move_to(_id_hidden_node.center)
    _ret['id'][1] = tikz.Node(
        id="id01",
        text_to_display=symbols.labelwithlk('id', '1'),
        anchor=tikz.Anchor.left(offset=_WIDTH * 0.2 / 5),
    )
    _path.add_node(_ret['id'][1])
    _path.move_to(_id_hidden_node.center)
    _ret['id'][2] = tikz.Node(
        id="id02",
        text_to_display=symbols.labelwithlk('id', '2'),
        anchor=tikz.Anchor.right(offset=_WIDTH * 0.2 / 5),
    )
    _path.add_node(_ret['id'][2])
    _path.move_to(_id_hidden_node.center)
    _ret['id'][3] = tikz.Node(
        id="id03",
        text_to_display=symbols.labelwithlk('id', '3'),
        anchor=tikz.Anchor.right(offset=_WIDTH * 0.2),
    )
    _path.add_node(_ret['id'][3])

    # ----------------------------------------- msb
    _ret['msb'] = {}
    _path.move_to(_msb_hidden_node.center)
    _ret['msb'][1] = tikz.Node(
        id="msb01",
        text_to_display=symbols.labelwithlk('msb', '1'),
        anchor=tikz.Anchor.below(offset=_WIDTH * 0.1),
    )
    _path.add_node(_ret['msb'][1])
    _ret['msb'][0] = tikz.Node(
        id="msb00",
        text_to_display=symbols.labelwithlk('msb', '0'),
        anchor=tikz.Anchor.above(offset=_WIDTH * 0.1),
    )
    _path.add_node(_ret['msb'][0])

    _tikz.add_path(_path)

    return _ret


def make_shaded_clusters(
    _tikz: tikz.TikZ, _point_nodes: t.Dict[int, t.List[tikz.Node]]):
    _path = tikz.Path(
        style=tikz.Style(
            fill=tikz.FillOptions(
                color=Color.gray(intensity=30),
            ),
            draw=tikz.DrawOptions(
                color=Color.gray(intensity=30),
                thickness=_WIDTH * 0.11,
                rounded_corners=_WIDTH * 0.01,
                arrow_def=tikz.ArrowDef(
                    start_tips=tikz.ArrowTip.round_cap,
                    end_tips=tikz.ArrowTip.round_cap,
                )
            ),
            # opacity=tikz.Opacity.nearly_transparent,
        )
    )

    _cluster_1_nodes = _point_nodes[0]
    _cluster_2_nodes = _point_nodes[1] + _point_nodes[2]
    _cluster_3_nodes = _point_nodes[3]

    # ----------------------------------------------- cluster 1
    _path.move_to(_cluster_1_nodes[0].center)
    for _index in [1, 3, 2]:
        _path.to(_cluster_1_nodes[_index].center)
    _path.cycle()

    # ----------------------------------------------- cluster 2
    _path.move_to(_cluster_2_nodes[0].center)
    for _index in [3, 6, 1, 5, 2, 7, 4]:
        _path.to(_cluster_2_nodes[_index].center)
    _path.cycle()

    # ----------------------------------------------- cluster 2
    _path.move_to(_cluster_3_nodes[0].center)
    for _index in [1, 3, 2]:
        _path.to(_cluster_3_nodes[_index].center)
    _path.cycle()

    _tikz.add_path(_path)


def make_point_nodes(
    _tikz: tikz.TikZ, apply_style: bool
) -> t.Dict[int, t.List[tikz.Node]]:
    _path = tikz.Path()
    _path.move_to(tikz.Point2D(_HEIGHT * 0.5, _WIDTH * 0.5))

    _ret = {}

    _coordinates = {
        0: [(0.21, 0.28), (0.30, 0.24), (0.33, 0.35), (0.39, 0.20), ],
        1: [(0.67, 0.22), (0.46, 0.57), (0.55, 0.50), (0.56, 0.29), ],
        2: [(0.70, 0.33), (0.47, 0.67), (0.52, 0.39), (0.62, 0.44), ],
        3: [(0.80, 0.56), (0.72, 0.60), (0.75, 0.68), (0.68, 0.77), ],
    }
    np.random.seed(1234)
    _iths = np.random.permutation(16)
    np.random.seed(None)

    for _label in range(4):
        _ret[_label] = []

        _color = {
            0: Color.teal, 1: Color.magenta, 2: Color.cyan, 3: Color.orange
        }[_label]

        if apply_style:
            _point_style = tikz.Style(
                draw=tikz.DrawOptions(
                    color=_color,
                    thickness=tikz.Thickness.thin
                ),
                fill=tikz.FillOptions(
                    color=_color(intensity=30)
                ),
                shape=tikz.Circle(),
            )
        else:
            _point_style = None

        for _p in range(4):
            _coordinate = tikz.Point2D(
                _WIDTH * _coordinates[_label][_p][0],
                _HEIGHT * _coordinates[_label][_p][1],
            )
            _path.move_to(_coordinate)
            _node_text = symbols.tracewithid(
                str(_iths[_label * 4 + _p]), str(_label))
            _node = tikz.Node(
                style=_point_style,
                id=f"point{_label}x{_p}" + ("xS" if apply_style else ""),
                text_to_display=f"\\footnotesize{{{_node_text}}}"
            )
            _path.add_node(_node)
            _ret[_label].append(_node)

    _tikz.add_path(_path)

    return _ret


def make_edges(
    _tikz: tikz.TikZ,
    _label_nodes: t.Dict[str, t.Dict[int, tikz.Node]],
    _point_nodes: t.Dict[int, t.List[tikz.Node]]
):
    _edge_style_easy = tikz.Style(
        draw=tikz.DrawOptions(
            color=Color.green,
            thickness=tikz.Thickness.thin,
            arrow_def=tikz.ArrowDef(
                end_tips=tikz.ArrowTip.latex,
            )
        )
    )
    _edge_style_difficult = tikz.Style(
        draw=tikz.DrawOptions(
            color=Color.red,
            dash_pattern=tikz.DashPattern.dashed,
            thickness=tikz.Thickness.thin,
            arrow_def=tikz.ArrowDef(
                end_tips=tikz.ArrowTip.latex,
            )
        )
    )

    _easy = {
        'hw': {
            0: {0: True, },
            1: {1: True, 2: True, },
            2: {3: True, },
        },
        'id': {
            0: {0: True, },
            1: {1: False, },
            2: {2: False, },
            3: {3: True, },
        },
        'msb': {
            0: {0: True, 2: False, },
            1: {1: False, 3: True, },
        },
        'lsb': {
            0: {1: False, 3: True, },
            1: {0: True, 2: False, },
        },
    }

    for _lk in _easy.keys():
        _labels = _easy[_lk]
        for _label in _labels.keys():
            _label_node = _label_nodes[_lk][_label]
            for _point in _labels[_label].keys():
                _point_node = _point_nodes[_point]
                if _labels[_label][_point]:
                    _edge_style = _edge_style_easy
                else:
                    _edge_style = _edge_style_difficult
                _path = tikz.Path(style=_edge_style)
                for _point_node in _point_nodes[_point]:
                    if _lk == "hw":
                        _label_anchor = _label_node.north
                    elif _lk == "lsb":
                        _label_anchor = _label_node.west
                    elif _lk == "id":
                        _label_anchor = _label_node.south
                    elif _lk == "msb":
                        _label_anchor = _label_node.east
                    else:
                        raise e.code.ShouldNeverHappen(msgs=[])
                    _path.move_to(_point_node.center).line_to(_label_anchor)
                _tikz.add_path(_path)

    # make legend
    _legend_path = tikz.Path()
    _ambig_legend_node = tikz.Node(
        id="ambignode", anchor=tikz.Anchor.below(offset=_HEIGHT * 0.01),
        text_to_display=FontSize.scriptsize("Ambiguous labels"),
        style=tikz.Style(
            shape=tikz.Rectangle(
                minimum_height=_HEIGHT * 0.05
            )
        )
    )
    _legend_path.move_to(_label_nodes['hw'][2].south)
    _legend_path.add_node(_ambig_legend_node)
    _nonambig_legend_node = tikz.Node(
        id="nonambignode", anchor=tikz.Anchor.below(offset=_HEIGHT * 0.01),
        text_to_display=FontSize.scriptsize("Learnable labels"),
        style=tikz.Style(
            shape=tikz.Rectangle(
                minimum_height=_HEIGHT * 0.05
            )
        )
    )
    _legend_path.move_to(_label_nodes['hw'][0].south)
    _legend_path.add_node(_nonambig_legend_node)

    _tikz.add_path(_legend_path)

    _ambig_legend_path = tikz.Path(style=_edge_style_difficult)
    _ambig_legend_path.move_to(_ambig_legend_node.south_west).line_to(_ambig_legend_node.south_east)
    _tikz.add_path(_ambig_legend_path)

    _nonambig_legend_path = tikz.Path(style=_edge_style_easy)
    _nonambig_legend_path.move_to(_nonambig_legend_node.south_west).line_to(_nonambig_legend_node.south_east)
    _tikz.add_path(_nonambig_legend_path)


def make_complicated_figure(scale: t.Tuple[float, float] = None):

    _tikz = tikz.TikZ(
        caption="Learnable Labels Vs. Ambiguous Labels", label="fig:ambig",
        positioning=Positioning(here=True, top=True, special_float_page=True),
        alignment=FloatObjAlignment.centering,
        scale=scale,
    )
    # _tikz.show_debug_grid(width=_WIDTH + .01, height=_HEIGHT, step=_STEP)

    _label_nodes = make_label_nodes(_tikz)

    _point_nodes = make_point_nodes(_tikz, apply_style=False)

    make_shaded_clusters(_tikz, _point_nodes)

    make_edges(_tikz, _label_nodes, _point_nodes)

    make_point_nodes(_tikz, apply_style=True)

    return _tikz


if __name__ == '__main__':

    _doc = Document()

    _doc.add_item(make_complicated_figure())

    _doc.write(save_to_file="try.tex", make_pdf=True)
