"""
Supporting tutorial: https://www.overleaf.com/learn/latex/TikZ_package

More official tutorial: https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf
We can convert this entirely ...

todo: Section 32 To Path Library ... support this ... looks useful
todo: Section 33 Tree Library    ... support this ... looks useful

todo: Section 22 Entity-Relationship Diagram Drawing Library
todo: Section 24 Matrix Library
todo: Section 25 Mindmap Drawing Library
todo: Section 28 Plot Handler Library
todo: Section 29 Plot Mark Library
"""

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Font, Scalar, Positioning, FloatObjAlignment


class Thickness(enum.Enum):
    """
    Refer:
    https://www.overleaf.com/learn/latex/TikZ_package
    """
    ultra_thin = "ultra thin"
    very_thin = "very thin"
    thin = "thin"
    semithick = "semithick"
    thick = "thick"
    very_thick = "very thick"
    ultra_thick = "ultra thick"

    def __str__(self) -> str:
        return self.value


class FillInteriorRule(enum.Enum):
    """
    Check section 12.3.2 Graphic Parameters: Interior Rules
    """
    nonzero_rule = "nonzero rule"
    even_odd_rule = "even odd rule"

    def __str__(self) -> str:
        return self.value


class Pattern(enum.Enum):
    """
    Check Section 26: Pattern Library
    """
    horizontal_lines = "horizontal lines"
    vertical_lines = "vertical lines"
    north_east_lines = "north east lines"
    north_west_lines = "north west lines"
    grid = "grid"
    crosshatch = "crosshatch"
    dots = "dots"
    crosshatch_dots = "crosshatch dots"
    fivepointed_stars = "fivepointed stars"
    sixpointed_stars = "sixpointed stars"
    bricks = "bricks"

    def __str__(self) -> str:
        return f"pattern={self.value}"


class Snake(enum.Enum):
    """
    Check section 31: Snake Library

    todo: Replace with decorations.pathmorphing library:
      https://tex.stackexchange.com/questions/42611/list-of-available-tikz-libraries-with-a-short-introduction/491626#491626
    """
    bent = "bent"
    border = "border"
    brace = "brace"
    bumps = "bumps"
    coil = "coil"
    expanding_waves = "expanding waves"
    saw = "saw"
    snake = "snake"
    ticks = "ticks"
    triangles = "triangles"
    crosses = "crosses"
    waves = "waves"
    zigzag = "zigzag"

    def __str__(self) -> str:
        return f"snake={self.value}"


class SnakeOptions(t.NamedTuple):
    """
    Check section 31: Snake Library
    Section 11.2.3 Snaked Lines

    todo: add validations to restrict some options bases on snake type ...
      As of now we allow all options but this can be restricted based on
      documentation ...
    """
    type: Snake = None

    gap_before_snake: Scalar = None
    gap_after_snake: Scalar = None
    gap_around_snake: Scalar = None

    line_before_snake: Scalar = None
    line_after_snake: Scalar = None
    line_around_snake: Scalar = None

    raise_snake: Scalar = None
    mirror_snake: bool = False

    segment_amplitude: Scalar = None
    segment_length: Scalar = None
    segment_object_length: Scalar = None
    segment_angle: t.Union[int, float] = None
    segment_aspect: t.Union[int, float] = None

    def __str__(self) -> str:
        _options = []

        if self.type is not None:
            _options.append(str(self.type))

        if self.gap_before_snake is not None:
            _options.append(f"gap before snake={self.gap_before_snake}")
        if self.gap_after_snake is not None:
            _options.append(f"gap after snake={self.gap_after_snake}")
        if self.gap_around_snake is not None:
            _options.append(f"gap around snake={self.gap_around_snake}")

        if self.line_before_snake is not None:
            _options.append(f"line before snake={self.line_before_snake}")
        if self.line_after_snake is not None:
            _options.append(f"line after snake={self.line_after_snake}")
        if self.line_around_snake is not None:
            _options.append(f"line around snake={self.line_around_snake}")

        if self.raise_snake is not None:
            _options.append(str(self.raise_snake))
        if self.mirror_snake:
            _options.append("mirror snake")

        if self.segment_amplitude is not None:
            _options.append(f"segment amplitude={self.segment_amplitude}")
        if self.segment_length is not None:
            _options.append(f"segment length={self.segment_length}")
        if self.segment_object_length is not None:
            _options.append(f"segment object length={self.segment_object_length}")
        if self.segment_angle is not None:
            _options.append(f"segment angle={self.segment_angle}")
        if self.segment_aspect is not None:
            _options.append(f"segment aspect={self.segment_aspect}")

        return ",".join(_options)


class ArrowTip(enum.Enum):
    """
    Check section 18: Arrow Tip Library
    """
    # special i.e. no arrow tip
    none = ""
    bar = '|'
    end_arrow = '>'  # defined/redefined through ArrowDef.end_arrow_kind
    start_arrow = '<'  # used swapped version of ArrowDef.end_arrow_kind

    # 18.1: Triangular Arrow Tips
    latex = "latex'"
    latex_reversed = "latex' reversed"
    stealth = "stealth'"
    stealth_reversed = "stealth' reversed"
    triangle_90 = 'triangle 90'
    triangle_90_reversed = 'triangle 90 reversed'
    triangle_60 = 'triangle 60'
    triangle_60_reversed = 'triangle 60 reversed'
    triangle_45 = 'triangle 45'
    triangle_45_reversed = 'triangle 45 reversed'
    open_triangle_90 = 'open triangle 90'
    open_triangle_90_reversed = 'open triangle 90 reversed'
    open_triangle_60 = 'open triangle 60'
    open_triangle_60_reversed = 'open triangle 60 reversed'
    open_triangle_45 = 'open triangle 45'
    open_triangle_45_reversed = 'open triangle 45 reversed'

    # 18.2: Barbed Arrow Tips
    angle_90 = 'angle 90'
    angle_90_reversed = 'angle 90 reversed'
    angle_60 = 'angle 60'
    angle_60_reversed = 'angle 60 reversed'
    angle_45 = 'angle 45'
    angle_45_reversed = 'angle 45 reversed'
    hooks = 'hooks'
    hooks_reversed = 'hooks reversed'

    # 18.3: Bracket-Like Arrow Tips
    square_bracket_open = '['
    square_bracket_close = ']'
    round_bracket_open = '('
    round_bracket_close = ')'

    # 18.4: Circle and Diamond Arrow Tips
    circle = "*"
    open_circle = "o"
    diamond = "diamond"
    open_diamond = "open diamond"

    # 18.5: Serif-Like Arrow Tips
    serif_cm = "serif cm"

    # 18.6: Partial Arrow Tips
    left_to = "left to"
    left_to_reversed = "left to reversed"
    right_to = "right to"
    right_to_reversed = "right to reversed"
    left_hook = "left hook"
    left_hook_reversed = "left hook reversed"
    right_hook = "right hook"
    right_hook_reversed = "right hook reversed"

    # 18.7: Line Caps
    # only visible when line width is too big i.e. say <line width=1ex>
    round_cap = "round cap"
    butt_cap = "butt cap"
    triangle_90_cap = "triangle 90 cap"
    triangle_90_cap_reversed = "triangle 90 cap reversed"
    fast_cap = "fast cap"
    fast_cap_reversed = "fast cap reversed"

    def __str__(self) -> str:
        return self.value


@dataclasses.dataclass
class ArrowDef:
    """
    todo: currently multiple arrows at start and end tip is not supported
          we need to implement redefining arrow syntax `>=⟨end arrow kind⟩` but that
          will force to have same repetitive symbol ... also note that arrow enum
          values that are of length more than 1 cannot be chained ... so only one tip
          can be used and multiple is possible by syntax `>=⟨end arrow kind⟩` but then
          we lose having various symbols
    """
    # tikz does not support start arrow kind, but you get swapped version of
    # this when used `<` instead of `>`
    end_arrow_kind: ArrowTip = None
    shorten_start: Scalar = None
    shorten_end: Scalar = None
    start_tips: t.Union[ArrowTip, t.List[ArrowTip], str, t.List[str]] = None
    end_tips: t.Union[ArrowTip, t.List[ArrowTip], str, t.List[str]] = None

    def __str__(self) -> str:
        _ret = []

        # ------------------------------------------------ 01
        # end_arrow_kind
        # todo: currently we are adding this to path options but we might
        #   also want only this part in scope options (\\begin{scope}[>=latex])
        #   and not the entire arrow defination
        if self.end_arrow_kind is not None:
            _ret.append(f">={self.end_arrow_kind}")

        # ------------------------------------------------ 02
        # shorten the start and end of arrow ... with tips provided this will already
        # shorten automatically bit you can control it further even when tips are
        # not provided
        if self.shorten_start is not None:
            _ret.append(f"shorten <={self.shorten_start}")
        if self.shorten_end is not None:
            _ret.append(f"shorten >={self.shorten_end}")

        # ------------------------------------------------ 03
        # make tip formatter
        _tip_format = ""
        if self.start_tips is not None:
            _tips = [self.start_tips] if isinstance(self.start_tips, ArrowTip) \
                else self.start_tips
            for _t in _tips:
                _tip_format += str(_t)
        _tip_format += '-'
        if self.end_tips is not None:
            _tips = [self.end_tips] if isinstance(self.end_tips, ArrowTip) \
                else self.end_tips
            for _t in _tips:
                _tip_format += str(_t)
        # i.e. when either start or end tips was provided
        if _tip_format != '-':
            _ret.append(_tip_format)

        # ------------------------------------------------ 04
        return ",".join(_ret)


class Cap(enum.Enum):
    round = "round"
    rect = "rect"
    butt = "butt"

    def __str__(self) -> str:
        return f"cap={self.value}"


class Opacity(enum.Enum):
    transparent = "transparent"
    ultra_nearly_transparent = "ultra nearly transparent"
    very_nearly_transparent = "very nearly transparent"
    nearly_transparent = "nearly transparent"
    semitransparent = "semitransparent"
    nearly_opaque = "nearly opaque"
    very_nearly_opaque = "very nearly opaque"
    ultra_nearly_opaque = "ultra nearly opaque"
    opaque = "opaque"

    def __str__(self) -> str:
        return f"{self.value}"


class Join(enum.Enum):
    round = "round"
    bevel = "bevel"
    miter = "miter"

    def __str__(self) -> str:
        return f"join={self.value}"

    def __call__(self, miter_limit: t.Union[int, float] = None) -> str:
        if miter_limit is not None:
            if self is self.miter:
                return f"join={self.value},miter limit={miter_limit}"
            else:
                raise e.code.CodingError(
                    msgs=[f"kwarg miter_limit is only allowed for {self.miter}"]
                )
        return f"join={self.value}"


class DashPattern(enum.Enum):
    solid = "solid"
    dotted = "dotted"
    densely_dotted = "densely dotted"
    loosely_dotted = "loosely dotted"
    dashed = "dashed"
    densely_dashed = "densely dashed"
    loosely_dashed = "loosely dashed"

    def __str__(self) -> str:
        return self.value


class TransformOptions(t.NamedTuple):
    rotate: t.Union[int, float] = None
    scale: t.Union[int, float] = None
    shift: 'Point' = None
    apply_current_external_transformation: bool = False

    def __str__(self):
        _options = []
        if self.rotate is not None:
            _options.append(f"rotate={self.rotate}")
        if self.scale is not None:
            _options.append(f"scale={self.scale}")
        if self.shift is not None:
            _options.append(f"shift={{{self.shift}}}")
        if self.apply_current_external_transformation:
            _options.append("transform shape")
        return ",".join(_options)


class FillOptions(t.NamedTuple):
    color: t.Union[Color, str] = None
    opacity: t.Union[int, float] = None
    pattern: Pattern = None
    pattern_color: t.Union[Color, str] = None
    fill_interior_rule: FillInteriorRule = None

    def __str__(self):
        _options = []
        if self.color is not None:
            _options.append(f"fill={self.color}")
        else:
            # needed if color not supplied
            _options.append("fill")
        if self.opacity is not None:
            _options.append(f"fill opacity={self.opacity}")
        if self.pattern is not None:
            _options.append(f"{self.pattern}")
        if self.pattern_color is not None:
            _options.append(f"pattern color={self.pattern_color}")
        if self.fill_interior_rule is not None:
            _options.append(str(self.fill_interior_rule))

        return ",".join(_options)


class Shade(enum.Enum):
    """
    Refer section 12.4.1 Choosing a Shading Type
    """
    axis = "axis"
    radial = "radial"
    ball = "ball"

    def __str__(self) -> str:
        return f"shading={self.value}"


class ShadeOptions(t.NamedTuple):
    """
    Check section 12.4 Shading a Path

    """
    type: Shade = None
    angle: t.Union[int, float] = None

    # ----------------------------------------------------------
    # following options' auto apply
    # shade
    # shading=axis
    # middle color is average of top and bottom color
    # shading angle=0
    top_color: t.Union[str, Color] = None
    bottom_color: t.Union[str, Color] = None
    # note that this will not change angle ... must be applied at last after
    # top and bottom as they affect it ... we have taken care of same
    middle_color: t.Union[str, Color] = None

    # ----------------------------------------------------------
    # same as top_color except that
    # shading angle=90
    left_color: t.Union[str, Color] = None
    right_color: t.Union[str, Color] = None

    # ----------------------------------------------------------
    # following options' auto apply
    # shade
    # shading=radial
    inner_color: t.Union[str, Color] = None
    outer_color: t.Union[str, Color] = None

    # ----------------------------------------------------------
    # following options' auto apply
    # shade
    # shading=ball
    ball_color: t.Union[str, Color] = None

    def __str__(self):
        # if this object is used means add shade keyword
        _options = ["shade"]

        if self.type is not None:
            _options.append(str(self.type))
        if self.angle is not None:
            _options.append(f"shading angle={self.angle}")
        if self.top_color is not None:
            _options.append(f"top color={self.top_color}")
        if self.bottom_color is not None:
            _options.append(f"bottom color={self.bottom_color}")
        if self.middle_color is not None:
            # note that middle must always be after top and bottom color
            _options.append(f"middle color={self.middle_color}")
        if self.left_color is not None:
            _options.append(f"left color={self.left_color}")
        if self.right_color is not None:
            _options.append(f"right color={self.right_color}")
        if self.inner_color is not None:
            _options.append(f"inner color={self.inner_color}")
        if self.outer_color is not None:
            _options.append(f"outer color={self.outer_color}")
        if self.ball_color is not None:
            _options.append(f"ball color={self.ball_color}")

        return ",".join(_options)


class DrawOptions(t.NamedTuple):
    color: t.Union[Color, str] = None
    opacity: t.Union[int, float] = None
    thickness: t.Union[Thickness, Scalar] = None
    cap: Cap = None
    join: Join = None
    dash_pattern: t.Union[DashPattern, t.List[t.Tuple[bool, Scalar]]] = None
    dash_phase: Scalar = None
    arrow_def: ArrowDef = None
    rounded_corners: Scalar = None
    # switches off any rounding on subsequent corners of the path
    sharp_corners: bool = False

    # section 12.2.5 Graphic Parameters: Double Lines and Bordered Lines
    # although in tikz it is `double` and `double distance` we name
    # differently for clarity ... as in reality to achieve double effect second line
    # is drawn over first line ...
    # Also note that second_thickness will affect first line thickness and is given as:
    #   thickness = 2 * thickness + second_thickness
    # If second_thickness not provided default of 0.6pt is used
    second_color: t.Union[Color, str] = None
    second_thickness: Scalar = None

    def __str__(self):
        _options = []
        if self.color is not None:
            _options.append(f"draw={self.color}")
        else:
            # needed if color not supplied
            _options.append("draw")
        if self.opacity is not None:
            _options.append(f"draw opacity={self.opacity}")
        if self.thickness is not None:
            if isinstance(self.thickness, Thickness):
                _options.append(str(self.thickness))
            else:
                _options.append(f"line width={self.thickness}")
        if self.cap is not None:
            _options.append(str(self.cap))
        if self.join is not None:
            _options.append(str(self.join))
        if self.dash_pattern is not None:
            if isinstance(self.dash_pattern, DashPattern):
                _options.append(str(self.dash_pattern))
            else:
                _options.append(
                    "dash pattern=" + " ".join(
                        f"{'on' if _1 else 'off'} {_2}"
                        for _1, _2 in self.dash_pattern
                    )
                )
        if self.dash_phase is not None:
            _options.append(f"dash phase={self.dash_phase}")
        if self.arrow_def is not None:
            _options.append(str(self.arrow_def))
        if self.rounded_corners is not None:
            _options.append(f"rounded corners={self.rounded_corners}")
        if self.sharp_corners:
            _options.append("sharp corners")
        if self.second_color is not None:
            _options.append(f"double={self.second_color}")
        if self.second_thickness is not None:
            _options.append(f"double distance={self.second_thickness}")
        return ",".join(_options)


class TextOptions(t.NamedTuple):
    color: Color = None
    opacity: t.Union[int, float] = None
    font: Font = None
    width: Scalar = None
    height: Scalar = None
    depth: Scalar = None
    justified: bool = False
    ragged: bool = False
    badly_ragged: bool = False
    centered: bool = False
    badly_centered: bool = False

    def __str__(self):
        _options = []
        if self.color is not None:
            _options.append(f"text={self.color}")
        if self.opacity is not None:
            _options.append(f"text opacity={self.opacity}")
        if self.font is not None:
            _options.append(f"font={self.font}")
        if self.width is not None:
            _options.append(f"text width={self.width}")
        if self.height is not None:
            _options.append(f"text height={self.height}")
        if self.depth is not None:
            _options.append(f"text depth={self.depth}")
        if self.justified:
            _options.append("text justified")
        if self.ragged:
            _options.append("text ragged")
        if self.badly_ragged:
            _options.append("text badly ragged")
        if self.centered:
            _options.append("text centered")
        if self.badly_centered:
            _options.append("text badly centered")
        return ",".join(_options)


@dataclasses.dataclass
class Shape(abc.ABC):
    """
    We refer to multiple sections from pdf

    Section 13.13 Predefined Shapes
      + Most of the things here we will make part of base Shape class
      + introduces basic shapes' rectangle, circle and coordinate

    Section 30: Shape Library ...
      + more shapes and respective anchors are specified

    Section 49: Nodes and Shapes
      + todo: not sure what this is about ... explore and add later

    Section 49.6 Predefined Shapes
      + covers anchors of base shapes
      + todo: make tutorials showing similar pictures with python code ...

    In this base class we will add fields that are common across many shapes

    Also, we will add anchors that are common across many shapes ...

    """
    inner_sep: Scalar = None
    inner_xsep: Scalar = None
    inner_ysep: Scalar = None
    outer_sep: Scalar = None
    outer_xsep: Scalar = None
    outer_ysep: Scalar = None
    minimum_height: Scalar = None
    minimum_width: Scalar = None
    minimum_size: Scalar = None

    def __str__(self):
        _options = []

        # here we add shape name inferred from class name
        _shape_name = " ".join(util.camel_case_split(self.__class__.__name__)).lower()
        _options.append(f"shape={_shape_name}")

        if self.inner_sep is not None:
            _options.append(f"inner sep={self.inner_sep}")
        if self.inner_xsep is not None:
            _options.append(f"inner xsep={self.inner_xsep}")
        if self.inner_ysep is not None:
            _options.append(f"inner ysep={self.inner_ysep}")

        if self.outer_sep is not None:
            _options.append(f"outer sep={self.outer_sep}")
        if self.outer_xsep is not None:
            _options.append(f"outer xsep={self.outer_xsep}")
        if self.outer_ysep is not None:
            _options.append(f"outer ysep={self.outer_ysep}")

        if self.minimum_height is not None:
            _options.append(f"minimum height={self.minimum_height}")
        if self.minimum_width is not None:
            _options.append(f"minimum width={self.minimum_width}")
        if self.minimum_size is not None:
            _options.append(f"minimum size={self.minimum_size}")

        return ",".join(_options)


class Rectangle(Shape):
    ...


class Circle(Shape):
    ...


class Diamond(Shape):
    aspect: float = None

    def __str__(self):
        _options = [super().__str__()]
        if self.aspect is not None:
            _options.append(f"aspect={self.aspect}")
        return ",".join(_options)


class Ellipse(Shape):
    ...


class RegularPolygon(Shape):
    sides: int = None
    rotate: t.Union[int, float] = None

    def __str__(self):
        _options = [super().__str__()]
        if self.sides is not None:
            _options.append(f"regular polygon sides={self.sides}")
        if self.rotate is not None:
            _options.append(f"regular polygon rotate={self.rotate}")
        return ",".join(_options)


class Star(Shape):
    points: int = None
    ratio: float = None
    height: Scalar = None
    rotate: t.Union[int, float] = None

    def __str__(self):
        _options = [super().__str__()]
        if self.points is not None:
            _options.append(f"star points={self.points}")
        if self.ratio is not None:
            _options.append(f"star point ratio={self.ratio}")
        if self.height is not None:
            _options.append(f"star point height={self.height}")
        if self.rotate is not None:
            _options.append(f"star rotate={self.rotate}")
        return ",".join(_options)


class ForbiddenSign(Shape):
    ...


class CircleSplit(Shape):
    ...


class CrossOut(Shape):
    ...


class StrikeOut(Shape):
    ...


class NodePos(enum.Enum):
    """
    Section 13.7
    """
    midway = "midway"  # pos=0.5
    near_start = "near start"  # pos=0.25
    near_end = "near end"  # pos=0.75
    very_near_start = "very near start"  # pos=0.125
    very_near_end = "very near end"  # pos=0.875
    at_start = "at start"  # pos=0
    at_end = "at end"  # pos=1

    def __str__(self):
        return self.value


class Style(t.NamedTuple):
    shape: Shape = None
    fill: FillOptions = None
    draw: DrawOptions = None
    snake: SnakeOptions = None
    shade: ShadeOptions = None

    # this opacity applies to all fill draw pattern shade ...
    # note that fill and draw options already have opacity field if you want to
    # control those separately
    opacity: t.Union[int, float, Opacity] = None

    def __str__(self) -> str:
        _options = []
        if self.shape is not None:
            _options.append(str(self.shape))
        if self.fill is not None:
            _options.append(str(self.fill))
        if self.draw is not None:
            _options.append(str(self.draw))
        if self.snake is not None:
            _options.append(str(self.snake))
        if self.shade is not None:
            _options.append(str(self.shade))
        if self.opacity is not None:
            if isinstance(self.opacity, Opacity):
                _options.append(str(self.opacity))
            else:
                _options.append(f"opacity={self.opacity}")
        return ",".join(_options)


class Anchor(enum.Enum):
    """
    Check section 13.5 Placing Nodes Using Anchors
    We support things  like
      + anchor ...
        (node is meaningless as we are anchoring on coordinate)
        (node_distance will have no use as anchors can be more
        that the special eight ... like mid, base, text and even angles ... so
        computing distance that radially outward is meaningless ... but we can still
        couple this with `shift` field of the parent node of this anchor)
      + above, above left, left ...
        (when node is None ... as we anchor over the coordinate on which the node
        using this anchor will be placed)
      + above of, above left of, left of ...
        (when node is not None i.e. we will anchor over points of specified node)
    Also note that we have @ coordinate support so that the anchor need not
    be specified as it uses tikz's `at` keyword

    node:
        When node is provided the `of` versions will be used
    node_distance:
        It is in direction of point_of_node i.e. x and y displacement is controlled ...
        Note that with @ we have different behaviour where we will call `Point.shift`
    """
    # (special anchors)
    angle = enum.auto()  # available with any shape
    side = enum.auto()  # available when node has shape regular polygon
    corner = enum.auto()  # available when node has shape regular polygon
    inner_point = enum.auto()  # available when node has shape star
    outer_point = enum.auto()  # available when node has shape star

    # (non-intuitive anchors)
    # todo: this does not have support for offset or node distance ... i.e. when using
    #  these anchors we cannot keep new node at some distance
    center = "center"
    east = "east"
    west = "west"
    north = "north"
    north_east = "north east"
    north_west = "north west"
    south = "south"
    south_east = "south east"
    south_west = "south west"
    text = "text"
    text_mid = "mid"
    text_mid_east = "mid east"
    text_mid_west = "mid west"
    text_base = "base"
    text_base_east = "base east"
    text_base_west = "base west"
    text_lower = "lower"  # available when node has shape CircleSplit

    # (intuitive anchors)
    above = "above"
    above_left = "above left"
    above_right = "above right"
    below = "below"
    below_left = "below left"
    below_right = "below right"
    left = "left"
    right = "right"

    @property
    def is_special(self) -> bool:
        return self in [
            self.angle, self.corner, self.side, self.inner_point, self.outer_point,
        ]

    @property
    def is_intuitive(self) -> bool:
        return self in [
            self.above, self.above_right, self.above_left,
            self.below, self.below_right, self.below_left,
            self.left, self.right,
        ]

    @property
    def is_non_intuitive(self) -> bool:
        return self in [
            self.center,
            self.east,
            self.west,
            self.north,
            self.north_east,
            self.north_west,
            self.south,
            self.south_east,
            self.south_west,
            self.text,
            self.text_mid,
            self.text_mid_east,
            self.text_mid_west,
            self.text_base,
            self.text_base_east,
            self.text_base_west,
            self.text_lower,
        ]

    def __str__(self) -> str:
        return self.__call__()

    def __call__(
        self,
        node: "Node" = None, offset: Scalar = None,
        angle: t.Union[int, float] = None,
        side: int = None, corner: int = None,
        inner_point: int = None, outer_point: int = None,
    ) -> str:
        """

        When node is supplied we will use `of` keyword

        If `offset` is supplied
          If node is supplied will be used as `node_distance`
            [above of=<node>, node distance=<offset>]
          Else will be used as above=<offset>
        """
        # ----------------------------------------------------- 01
        # some vars
        _is_special = self.is_special
        _is_non_intuitive = self.is_non_intuitive
        _is_intuitive = self.is_intuitive
        # node and offset is only supported for intuitive anchors ...
        # We need some validations for below statements
        # + for non-intuitive anchors - node supported but not offset
        # + for special anchors - node supported but not offset
        # + for intuitive anchors - node supported and offset supported
        # todo: verify the above comment
        if _is_special or _is_non_intuitive:
            if offset is not None:
                raise e.code.CodingError(
                    msgs=[
                        "Looks like a special or non-intuitive anchor",
                        f"Please so not supply kwarg `offset` for anchor {self}"
                    ]
                )
        # if node is provided make sure that id is available
        if node is not None:
            if node.name is None:
                e.code.CodingError(
                    msgs=["Please use node's that have id defined ..."]
                )

        # ----------------------------------------------------- 02
        # for special anchors
        if _is_special:
            if self is self.angle:
                if angle is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `angle` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                if node is None:
                    return f"anchor={angle}"
                else:
                    return f"{node.name}.{angle}"
            if self is self.side:
                if side is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `side` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                if node is None:
                    return f"anchor=side {side}"
                else:
                    return f"{node.name}.side {side}"
            if self is self.corner:
                if corner is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `corner` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                if node is None:
                    return f"anchor=corner {corner}"
                else:
                    return f"{node.name}.corner {corner}"
            if self is self.inner_point:
                if inner_point is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `inner_point` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                if node is None:
                    return f"anchor=inner point {inner_point}"
                else:
                    return f"{node.name}.inner point {inner_point}"
            if self is self.outer_point:
                if outer_point is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `outer_point` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                if node is None:
                    return f"anchor=outer point {inner_point}"
                else:
                    return f"{node.name}.outer point {inner_point}"

        # ----------------------------------------------------- 03
        # _is_non_intuitive
        if _is_non_intuitive:
            if angle is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `angle` for non-intuitive "
                          f"anchor {self}"]
                )
            if side is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `side` for non-intuitive "
                          f"anchor {self}"]
                )
            if corner is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `corner` for non-intuitive "
                          f"anchor {self}"]
                )
            if inner_point is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `inner_point` for non-intuitive "
                          f"anchor {self}"]
                )
            if outer_point is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `outer_point` for non-intuitive "
                          f"anchor {self}"]
                )
            if node is None:
                return f"anchor={self.value}"
            else:
                return f"{node.name}.{self.value}"

        # ----------------------------------------------------- 04
        # if `node` is not provided then do not use `of` behaviour and use kwarg
        # `offset` as `offset`
        if _is_intuitive:
            if node is None:
                if offset is None:
                    return f"{self.value}"
                else:
                    return f"{self.value}={offset}"
            # if `node` is provided then use `of` and use kwarg `offset` if
            # provided as `node distance`
            else:
                if offset is None:
                    return f"{self.value} of={node.name}"
                else:
                    return f"{self.value} of={node.name}, node distance={offset}"

        # ----------------------------------------------------- 05
        raise e.code.CodingError(
            msgs=[
                f"Anchor {self} is neither intuitive, non-intuitive nor special ..."
            ]
        )


@dataclasses.dataclass
class Point(abc.ABC):
    """
    Point are like coordinate that are lightweight nodes without shape and `at` part
    can be missed as it infers it
    \\path ... coordinate[⟨options⟩](⟨name⟩)at(⟨coordinate⟩) ...;

    This is same as
    node[shape=coordinate][⟨options⟩](⟨name⟩)at(⟨coordinate⟩){},
    """

    def __post_init__(self):
        # set var
        # noinspection PyTypeChecker
        self._tikz = None  # type: TikZ

    def __str__(self):
        raise e.code.NotAllowed(
            msgs=[f"Please override in child class {self.__class__}"]
        )

    def __add__(self, other: "Point") -> str:
        return f"($ {self} + {other} $)"

    def midway_point(self, other_point: "Point", ratio: float) -> str:
        return f"($ {self}!{ratio}!{other_point} $)"

    @classmethod
    def between_nodes(cls, node1: "Node", node2: "Node", ratio: float) -> str:
        return node1.pt_center.midway_point(node2.pt_center, ratio=ratio)

    def shift(
            self,
            x: Scalar = Scalar(0),
            y: Scalar = Scalar(0),
            z: Scalar = Scalar(0),
    ) -> str:
        _str = str(self)

        _first_brace_index = _str.find("(") + 1

        _shift_token = f"[shift={{({x},{y},{z})}}]"

        _ret = _str[:_first_brace_index] + _shift_token + _str[_first_brace_index:]

        return _ret


@dataclasses.dataclass
class Point2D(Point):
    """
    Coordinate system: canvas (section 10.2.1)
      Explicit: \\fill (canvas cs:x=1cm,y=1.5cm) circle (2pt);
      Implicit: \\fill (x=1cm,y=1.5cm) circle (2pt);

    Also read:
    Section 8.1: Special Syntax For Specifying Points
    Section 10: Specifying Coordinates
    https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf

    We aim to keep everything in pt instead of cm
    Since we do not specify anything it is always pt in tikz ...
    to convert to cm just multiply by ratio 1cm/1pt

    Also, everywhere we use coordinate system implicitly so that the generated tex
    file are not verbose

    relative:
      For example,
        (1,0) ++(1,0) ++(0,1) specifies the three coordinates
        (1,0), then (2,0), and (2,1).
      For example,
        (1,0) +(1,0) +(0,1) specifies the three coordinates
        (1,0), then (2,0), and (1,1).

    id:
      If provided we assume that you might want to use it by id later, so we will add
      coordinate name to it ... note that if you want something complex then use Node
    """
    x: Scalar
    y: Scalar
    relative: t.Literal['+', '++', ''] = ''
    id: str = None

    def __str__(self):
        _ret = f"{self.relative}({self.x},{self.y})"
        if self.id is not None:
            _ret += f" coordinate ({self.id})"
        return _ret


@dataclasses.dataclass
class Point3D(Point):
    """
    Coordinate system: xyz (section 10.2.1)
      Explicit: \\draw (0,0) -- (xyz cs:x=1);
                \\draw (0,0) -- (xyz cs:z=1);
      Implicit: \\draw (0,0) -- (1, 0);
                \\draw (0,0) -- (0, 0, 1);
    """
    x: Scalar
    y: Scalar
    z: Scalar
    relative: t.Literal['+', '++'] = ''
    id: str = None

    def __str__(self):
        _ret = f"{self.relative}({self.x},{self.y},{self.z})"
        if self.id is not None:
            _ret += f" coordinate ({self.id})"
        return _ret


@dataclasses.dataclass
class PointPolar(Point):
    """
    Coordinate system: canvas polar (section 10.2.1)
      Explicit: \\draw (0,0) -- (canvas polar cs:angle=30,radius=1cm);
                \\draw (0,0) -- (canvas polar cs:angle=30,x radius=1cm,y radius=2cm);
      Implicit: \\draw (0,0) -- (30:1cm and 2cm);

    When you provide an x-radius and also a y-radius, you specify an ellipse instead
    of a circle. The radius option has the same effect as specifying identical
    x radius and y radius options.

    todo: `xyz polar` and `xy polar` coordinate system ...
           the implicit notation is same to `canvas polar`
           radius and the angle are interpreted in the xy-coordinate system
           dont know what that means explore later if needed
    """
    angle: t.Union[int, float]
    radius: t.Union[Scalar, t.Tuple[Scalar, Scalar]]
    relative: t.Literal['+', '++'] = ''
    id: str = None

    def __str__(self):
        if isinstance(self.radius, tuple):
            # when tuple we expect both to be supplied and assume that they
            # will be different ... acts as x radius and y radius
            _ret = f"{self.relative}" \
                   f"({self.angle}:{self.radius[0]} and {self.radius[1]})"
        else:
            _ret = f"{self.relative}({self.angle}:{self.radius})"
        if self.id is not None:
            _ret += f" coordinate ({self.id})"
        return _ret


@dataclasses.dataclass
class PointOnNode(Point):
    """
    Coordinate system: node cs (section 10.2.3)

    Helps you get coordinates around/on Node with similar syntax as that of
    <Point*> classes

    Explicit:
      \\node (shape) at (0,2) [draw] {|class Shape|};
      \\draw (node cs:name=shape,anchor=north) |- (0,1);
      \\draw (node cs:name=shape,angle=90) |- (0,1);
    Implicit:
      \\draw (shape.north) |- (0,1);
      \\draw (shape.90) |- (0,1);

    todo: When you do not supply node we assume it is previously defined shape on which
      you are requesting anchor ... as in (first node.south).
    """
    node: "_Node"
    anchor: Anchor = None
    angle: t.Union[int, float] = None
    side: int = None
    corner: int = None
    inner_point: int = None
    outer_point: int = None

    def __post_init__(self):
        # call super
        super().__post_init__()

        # test if one of four file is supplied
        if sum(
            [self.anchor is None, self.angle is None,
             self.side is None, self.corner is None,
             self.inner_point is None, self.outer_point is None]
        ) == 3:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Only supply only one of the six fields ..."
                ]
            )

        # expecting node id to be available
        if self.node.name is None:
            raise e.validation.NotAllowed(
                msgs=[
                    "Cannot provide point on this node as it does not have "
                    "`id` specified ..."
                ]
            )

        # expecting anchor used to be non-intuitive
        if self.anchor is not None:
            if not self.anchor.is_non_intuitive:
                raise e.validation.NotAllowed(
                    msgs=["Only use non-intuitive anchor ... for special anchors use "
                          "other fields of this dataclass"]
                )

    def __str__(self) -> str:
        if self.anchor is not None:
            # Note that if Anchor then __str__ can handle
            # only if using non-intuitive anchors
            return f"({self.anchor(node=self.node)})"
        elif self.angle is not None:
            # noinspection PyCallingNonCallable
            return f"({Anchor.angle(node=self.node)})"
        elif self.side is not None:
            # noinspection PyCallingNonCallable
            return f"({Anchor.side(node=self.node)})"
        elif self.corner is not None:
            # noinspection PyCallingNonCallable
            return f"({Anchor.corner(node=self.node)})"
        elif self.inner_point is not None:
            # noinspection PyCallingNonCallable
            return f"({Anchor.inner_point(node=self.node)})"
        elif self.outer_point is not None:
            # noinspection PyCallingNonCallable
            return f"({Anchor.outer_point(node=self.node)})"
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown {self}"])


@dataclasses.dataclass
class _Node(abc.ABC):

    # id
    # we are keeping this mandatory but latex does not need it
    # having unique name allows debugging
    # todo: add mechanism to auto generate id when made optional
    name: str = None

    # refer section 17.4: The Node Text
    text: str = None

    @property
    def pt_center(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.center)

    @property
    def pt_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.east)

    @property
    def pt_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.west)

    @property
    def pt_north(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north)

    @property
    def pt_north_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north_east)

    @property
    def pt_north_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north_west)

    @property
    def pt_south(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south)

    @property
    def pt_south_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south_east)

    @property
    def pt_south_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south_west)

    @property
    def pt_text(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text)

    @property
    def pt_text_mid(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid)

    @property
    def pt_text_mid_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid_east)

    @property
    def pt_text_mid_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid_west)

    @property
    def pt_text_base(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base)

    @property
    def pt_text_base_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base_east)

    @property
    def pt_text_base_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base_west)

    @property
    def pt_text_lower(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_lower)

    def pt_at_angle(self, angle: t.Union[int, float]) -> PointOnNode:
        return PointOnNode(node=self, angle=angle)

    def pt_on_side(self, side: int) -> PointOnNode:
        return PointOnNode(node=self, side=side)

    def pt_on_corner(self, corner: int) -> PointOnNode:
        return PointOnNode(node=self, corner=corner)

    def pt_on_inner_point(self, inner_point: int) -> PointOnNode:
        return PointOnNode(node=self, inner_point=inner_point)

    def pt_on_outer_point(self, outer_point: int) -> PointOnNode:
        return PointOnNode(node=self, outer_point=outer_point)


@dataclasses.dataclass
class Label(_Node):
    """
    Although not a subclass of Node this is still a Node in latex

    Section 13.9 The Label and Pin Options
    label=[⟨options⟩]⟨angle⟩:⟨text⟩

    Section 17.10.2 The Label Option
    /tikz/label=[〈options〉]〈angle〉:〈text〉

    Even you can name these nodes to be reused later
    \\begin{tikzpicture}
    \\node [circle,draw,label={[name=label node]above left:$a,b$}] {};
    \\draw (label node) -- +(1,1);
    \\end{tikzpicture}
    """

    style: Style = None
    angle: t.Union[int, float] = None
    anchor: Anchor = None  # must be only intuitive anchors
    # todo: this also needs to go in tikz options global to tikz picture
    distance: Scalar = None

    _node: "Node" = None

    def __post_init__(self):
        # validation
        if self.angle is not None and self.anchor is not None:
            raise e.code.CodingError(
                msgs=["only supply one of angle or anchor kwarg"]
            )
        if self.anchor is not None:
            if not self.anchor.is_intuitive:
                raise e.code.CodingError(
                    msgs=["Only intuitive anchors are supported"]
                )

    def __str__(self):
        if self._node is None:
            raise e.code.CodingError(
                msgs=[
                    "This label was never attached to any node"
                ]
            )
        _l = "label={"
        _options = []
        if bool(self.name):
            _options.append(f"name={self.name}")
        if self.distance is not None:
            _options.append(f"label distance={self.distance}")
        if self.style is not None:
            _options.append(str(self.style))
        _l += "[" + ",".join(_options) + "]"
        if self.anchor is not None:
            # as the __str__ is formatted for normal options use self.anchor.value
            _l += str(self.anchor.value)
        if self.angle is not None:
            _l += str(self.angle)
        if bool(self.text):
            _l += f":{self.text}" + "}"
        else:
            _l += "}"
        return _l


@dataclasses.dataclass
class Pin(_Node):
    """
    Although not a subclass of Node this is still a Node in latex

    Section 13.9 The Label and Pin Options
    pin=[⟨options⟩]⟨angle⟩:⟨text⟩

    17.10.3 The Pin Option
    /tikz/pin=[〈options〉]〈angle〉:〈text〉
    """

    style: Style = None
    angle: t.Union[int, float] = None
    anchor: Anchor = None
    # todo: this also needs to go in tikz options global to tikz picture
    distance: Scalar = None
    edge_style: Style = None

    _node: "Node" = None

    def __post_init__(self):
        # validation
        if self.angle is not None and self.anchor is not None:
            raise e.code.CodingError(
                msgs=["only supply one of angle or anchor kwarg"]
            )
        if self.anchor is not None:
            if not self.anchor.is_intuitive:
                raise e.code.CodingError(
                    msgs=["Only non-intuitive anchors are supported"]
                )

    def __str__(self):
        if self._node is None:
            raise e.code.CodingError(
                msgs=[
                    "This pin was never attached to any node"
                ]
            )
        _l = "pin={"
        _options = []
        if bool(self.name):
            _options.append(f"name={self.name}")
        if self.distance is not None:
            _options.append(f"pin distance={self.distance}")
        if self.style is not None:
            _options.append(str(self.style))
        if self.edge_style is not None:
            _options.append(f"pin edge={{{self.edge_style}}}")
        _l += "[" + ",".join(_options) + "]"
        if self.anchor is not None:
            # as the __str__ is formatted for normal options use self.anchor.value
            _l += str(self.anchor.value)
        if self.angle is not None:
            _l += str(self.angle)
        if bool(self.text):
            _l += f":{self.text}" + "}"
        else:
            _l += "}"
        return _l


@dataclasses.dataclass
class Node(_Node):
    """

    14.17 The Node and Edge Operations
    17 Nodes and Edges

    The node operation adds a so-called node to a path. This operation is
    special in the following sense: It does not change the current path
    in any way. In other words, this operation is not really a path
    operation, but has an effect that is “external” to the path.

    The edge operation has similar effect in that it adds something after
    the main path has been drawn. However, it works like the to operation,
    that is, it adds a to path to the picture after the main path has been
    drawn. Since these operations are quite complex, they are described
    in the separate Section 17.

    Note that the Node also can be used as coordinate ...
    use it as it is smart than just using coordinate
    + 17.11 Connecting Nodes: Using Nodes as Coordinates


    https://tikz.dev/tikz-shapes
    \path … node ⟨foreach statements⟩ [⟨options⟩] (⟨name⟩) at(⟨coordinate⟩) :⟨animation attribute⟩={⟨options⟩} {⟨node contents⟩} …;

    Understanding points on Node
      The properties/methods that return `PointOnNode` please refer section 49.6

    The LaTeX syntax:
      \\path ... node[⟨options⟩](⟨name⟩)at(⟨coordinate⟩){⟨text⟩} ...;

    todo: support multi-part nodes (see section 13.3)

    todo: based on `o_node.shape` the anchor points differ ... so add
      more properties or make a dict of new anchors
      Check section 30: Shape Library ... to see complete list of new anchors
      for given shape
    """

    # refer section 17.4: The Node Text
    text: str = None  # optional for Node

    # style
    style: t.Union[str, Style] = None
    # refer section 17.4: The Node Text
    o_text: TextOptions = None
    o_transform: TransformOptions = None

    # Refer: 13.5: Placing Nodes Using Anchors
    # with this field we address all below latex node options
    #  anchor, above, above left, left ... above of, above left of, left of ...
    # this will only anchor current node at specific node.anchor (i.e. PointOnNode)...
    # but for generic coordinates use @ operator ... which uses special
    # `at` latex keyword
    # What it does ??
    # causes the node to be shifted such that it’s anchor ⟨anchor name⟩ lies on the
    # current coordinate.
    anchor: t.Union[str, Anchor] = None

    # Section 13.7 Placing Nodes on a Line or Curve Explicitly
    # -----
    # when used the node is not anchored on last coordinate but somewhere on last
    # path based on this fraction ...
    # if previous path is line_to: then it is simple
    # if previous path is curve_to: this is the time travelled over path
    # if previous path is line_hv_to or line_vh_to then 0.5 is exactly corner
    # for all remaining paths position placement does not work
    # for arc path this might work in future
    pos_on_last_path: t.Union[float, NodePos] = None
    # -----
    # auto: <direction> = None
    # todo: auto ... must go in tikzpicture options
    # -----
    # this works when auto positioning is used and does the role of swapping the node
    # anchoring behaviour
    swap: bool = False
    # -----
    # used when adding label on path so that they are parallel to path
    # The rotation is normally done in such a way that text is never "upside down".
    # To get upside-down text, use can use [rotate=180] or [allow upside down]
    sloped: bool = False
    # -----
    # If set to true, TikZ will not "righten" upside down text.
    # todo: may be must go in tikzpicture options
    allow_upside_down: bool = False

    labels: t.List[Label] = dataclasses.field(default_factory=list)
    pins: t.List[Pin] = dataclasses.field(default_factory=list)

    def __post_init__(self):

        # please refer section 49.6 to see what anchors are available on node ...
        # this also varies based on shape used (todo: add checks later)
        # todo: based on shape test anchor ... certain anchors are available
        #  based on shape
        # if _style is not None:
        #     _shape = _style.shape
        #     if self.anchor in [
        #       Anchor.corner, Anchor.side] ... this will become str so wont work

        # add some vars
        self._at = None

        # set var
        # noinspection PyTypeChecker
        self._tikz = None  # type: TikZ

        # test labels and pins and set _node
        if bool(self.labels):
            for _l in self.labels:
                if _l._node is not None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"The label is already used by node {_l._node.name}"
                        ]
                    )
                _l._node = self
        if bool(self.pins):
            for _p in self.pins:
                if _p._node is not None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"The pin is already used by node {_p._node.name}"
                        ]
                    )
                _p._node = self

    def __matmul__(self, other: Point) -> "Node":
        """
        We use new @ operator for `at` tikz keyword
        """
        if self._at is None:
            self._at = other
        else:
            raise e.code.CodingError(
                msgs=[f"This node {self} is already positioned at {self._at}"]
            )
        return self
        # _kwargs = {
        #     _f.name: getattr(self, _f.name) for _f in dataclasses.fields(self)
        # }
        # # noinspection PyArgumentList
        # _ret = self.__class__(**_kwargs)
        # _ret._at = other
        # _ret.id = None  # as this is new Node
        # return _ret

    def __str__(self):
        """
        The LaTeX syntax:
          \\path ... node[⟨options⟩](⟨name⟩)at(⟨coordinate⟩){⟨text⟩} ...;
        """
        # -------------------------------------------------------- 01
        # validation
        # when style key provided check if it is registered ...
        _style = self.style
        if isinstance(_style, str):
            e.validation.ShouldBeOneOf(
                value=_style, values=list(self._tikz.styles.keys()),
                msgs=[f"Style {_style} si not registered with tikz_context"]
            ).raise_if_failed()
            _style = self._tikz.styles[_style]

        # -------------------------------------------------------- 02
        # the token to return
        if self._at is None:
            _ret = "node "
        else:
            _ret = f"node at {self._at} "

        # add id if specified
        if bool(self.name):
            _ret += f"({self.name})"

        # -------------------------------------------------------- 03
        # make options
        _options = []
        if self.pos_on_last_path is not None:
            if isinstance(self.pos_on_last_path, NodePos):
                _options.append(str(self.pos_on_last_path))
            else:
                _options.append(f"pos={self.pos_on_last_path}")
        if self.swap:
            _options.append("swap")
        if self.sloped:
            _options.append("sloped")
        if self.allow_upside_down:
            _options.append("allow upside down")
        if self.style is not None:
            _options.append(str(self.style))
        if self.o_text is not None:
            _options.append(str(self.o_text))
        if self.o_transform is not None:
            _options.append(str(self.o_transform))
        if self.anchor is not None:
            _options.append(str(self.anchor))
        for _l in self.labels:
            _options.append(str(_l))
        for _p in self.pins:
            _options.append(str(_p))
        _ret += "[" + ",".join(_options) + "] "

        # -------------------------------------------------------- 04
        # finally, add text value if supplied
        if self.text is not None:
            _ret += "{" + self.text + "}"
        else:
            _ret += "{}"

        # -------------------------------------------------------- 05
        # return
        return _ret

    def position_at(self, other: t.Union[Point, str]) -> "Node":
        self @ other  # check __matmul__
        return self


@dataclasses.dataclass
class Path:
    """
    14: Syntax for Path Specifications

    Most important component for TikZ class.
    Path can have
      Point (i.e. tikz coordinate)
      Node (i.e. tikz node) ... note that Point is Node with shape=coordinate
                                but use coordinate when you do not need extra stuff
                                also you need not supply empty braces

    Path can have its components connected by
      Path.connect  (i.e. tikz '--')
      Path.connect_HV (i.e. tikz '-|')
      Path.connect_VH (i.e. tikz '|-')
      Path.connect_hidden
        (i.e. in tikz we just place two coordinated side by side,
        equivalent to add space ... ' ' this is cheat, but it is completely fine)

    Actions on path:
      draw (draws a line with specified thickness)
      fill (interior of the specified gets colored ... assumes a closed path)
      shade
      clip
      or any combo of above all

    NOTE:
        We simplify our code and use only path as generic method. We don't need
        to support abbreviations like \\draw, \\fill, \\filldraw
    """
    style: t.Union[str, Style] = None

    # actions check section 12 Action on Paths
    # color -- we do not want to support this action due to confusion involved simple
    #          use only fill to get same effect
    # action [1] -------------------------------------
    # o_draw: DrawOptions = None ... Use via Style
    # action [2] -------------------------------------
    # o_fill: FillOptions = None ... Use via Style
    # action [3] -------------------------------------
    # supported in FillOptions ... todo: maybe we want it iin separate PatternOptions
    # pattern
    # action [4] -------------------------------------
    # clip .. see section 12.6 Using a Path For Clipping
    clip: bool = False
    # action [5] -------------------------------------
    # same as fill ... makes sense along with draw ...
    # with fill works but makes no sense ...
    # make sure you use either fill or shade ...
    # also maybe pattern does not work with fill ...
    # todo: add validation for this
    #  ... either use pattern, shade or fill
    #  ... based on more understanding
    # o_shade: ShadeOptions = None ... Use via Style
    # action [6] -------------------------------------
    # use this path as bounding box
    use_as_bounding_box: bool = False

    # this opacity applies to all fill draw pattern shade ...
    # note that fill and draw options already have opacity field if you want to
    # control those path actions separately
    # opacity: t.Union[int, float, Opacity] = None ... Use via Style

    # transform options at path level
    o_transform: TransformOptions = None

    # configure snake
    # o_snake: SnakeOptions = None ... Use via Style

    def __post_init__(self):
        # container to save all segments of path
        self.connectome = []

        # set var
        # noinspection PyTypeChecker
        self._tikz = None  # type: TikZ

    def __str__(self):
        # ---------------------------------------------------------- 01
        # return str
        _ret = "\\path"
        # keep reference for _tikz ...
        # __str__ is like build, so we do these assignments here
        for _pi in self.connectome:
            if isinstance(_pi, str):
                continue
            if _pi._tikz is None:
                _pi._tikz = self._tikz
            else:
                if id(_pi._tikz) != id(self._tikz):
                    raise e.code.CodingError(
                        msgs=["_tikz was already set ... "
                              "and is not same as new value you want to set",
                              "We expect the nodes to be from same tikz picture"]
                    )

        # ---------------------------------------------------------- 02
        # make options
        _options = []
        if self.style is not None:
            _options.append(str(self.style))
        if self.o_transform is not None:
            _options.append(str(self.o_transform))
        if self.use_as_bounding_box:
            _options.append("use as bounding box")
        if self.clip:
            _options.append("clip")
        _ret += "[" + ",".join(_options) + "] "

        # ---------------------------------------------------------- 03
        # process connectome
        for _item in self.connectome:
            _ret += str(_item) + " "

        # ---------------------------------------------------------- 04
        return _ret + ";"

    def add_node(self, node: _Node) -> "Path":
        # todo: if not needed remove this method
        raise e.code.CodingError(
            msgs=["Although adding nodes in path is possible but for now we block it",
                  "Prefer registering nodes directly with TikZ"]
        )
        # the below code works and new nodes to path
        # for now we comment it
        # self.connectome += [node]
        # return self

    def add_point(self, point: Point) -> "Path":
        self.connectome += [point]
        return self

    def move_to(self, to: t.Union[Point, _Node]) -> "Path":
        """

        Section 14.1 The Move-To Operation
        \\path . . . ⟨coordinate⟩ . . . ;
        In the specification (0,0) --(2,0) (0,1) --(2,1) two move-to operations
          are specified: (0,0) and (0,1). The other two operations,
          namely --(2,0) and --(2,1) are line-to operations

        """
        self.connectome += [to]
        return self

    def move_back(self) -> "Path":
        """
        Section 14.1 The Move-To Operation

        There is special coordinate called current subpath start that is
        always at the position of the last move-to operation on the current path.

        \tikz [line width=2mm] \draw (0,0) --(1,0) --(1,1) --(0,1) --(current subpath start) ;

        Note how in the above example the path is not closed (as --cycle would do).
        Rather, the line just starts and ends at the origin without being a closed path.
        """
        self.connectome += ["-- (current subpath start)"]
        return self

    def line_to(
        self,
        to: t.Union[Point, _Node],
        connect_type: t.Literal['--', '|-', '-|'] = '--',
        nodes: t.List[Node] = None
    ) -> "Path":
        """
        Section 14.2 The Line-To Operation
        \\path . . . --⟨coordinate⟩ . . . ;  # straight lines
        \\tikz {\\draw (0,0) to[line to] (1,0);}

        Automatic anchors are computed for the same ...
        while center is used for other path commands like parabola, plot etc.

        Note: the nodes options here ...
              they are more specifically to be used as labels on drawn path ...
              Read: 13.8 Placing Nodes on a Line or Curve Implicitly
              todo: maybe we do not need nodes as we can add later and set pos=... on it
                Read: 13.8 Placing Nodes on a Line or Curve Implicitly
                We might have limitations and also it places nodes not exactly at end
                and sets the nodes pos automatically and they get locked

        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        if bool(nodes):
            self.connectome += [connect_type, nodes, to]
        else:
            self.connectome += [connect_type, to]
        return self

    def cycle(self) -> "Path":
        """
        Section 14.2 The Line-To Operation
        Cycles the path. Useful for closed figures

        \\begin{tikzpicture}[line width=10pt]
        \\draw (0,0) --(1,1) --(1,0) --(0,0) (2,0) --(3,1) --(3,0) --(2,0) ;
        \\draw (5,0) --(6,1) --(6,0) -- cycle (7,0) --(8,1) --(8,0) -- cycle;
        \\useasboundingbox (0,1.5); % make bounding box higher
        \\end{tikzpicture}

        """
        self.connectome += ["cycle"]
        return self

    def curve_to(
        self,
        to: t.Union[Point, _Node],
        control1: Point, control2: Point = None,
        nodes: t.List[Node] = None,
    ) -> "Path":
        """
        Section 14.3 The Curve-To Operation
        \\path ... ..controls〈c〉and〈d〉..〈y or cycle〉 ...;

        The curve-to operation allows you to extend a path using a B´ezier curve.

        Automatic anchors are computed for the same ...
        while center is used for other path commands like parabola, plot etc.

        If the "and⟨d⟩" part is not given, d is assumed to be equal to c.

        Note: the nodes options here ... todo: needs testing
              they are more specifically to be used as labels on drawn path ...
              todo: maybe we do not need nodes as we can add later and set pos=... on it
                Read: 13.8 Placing Nodes on a Line or Curve Implicitly
                We might have limitations and also it places nodes not exactly at end
                and sets the nodes pos automatically and they get locked

        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        if control2 is None:
            _p = f"..controls{control1}.."
        else:
            _p = f"..controls{control1}and{control2}.."
        if bool(nodes):
            self.connectome += [_p, nodes, to]
        else:
            self.connectome += [_p, to]
        return self

    def draw_rectangle(self, corner: t.Union[Point, _Node]) -> "Path":
        """
        Section 14.4 The Rectangle Operation
        \\path ... rectangle〈corner or cycle〉 ...;

        A rectangle can obviously be created using four straight lines and a
        cycle operation. However, since rectangles are needed so often, a
        special syntax is available for them.
        """
        if isinstance(corner, _Node):
            corner = f"({corner.name})"
        self.connectome += [f"rectangle {corner}"]
        return self

    def set_rounded_corners(self, inset: Scalar = None) -> "Path":
        """
        Section 14.5 Rounding corners
        """
        if inset is None:
            self.connectome += ["rounded corners"]
        else:
            self.connectome += [f"rounded corners={inset}"]
        return self

    def set_sharp_corners(self) -> "Path":
        """
        Section 14.5
        This options switches off any rounding on subsequent corners of the path.

        \\begin{tikzpicture}
        \\draw (0,0) [rounded corners=10pt]
        -- (1,1) -- (2,1) [sharp corners]
        -- (2,0) [rounded corners=5pt] -- cycle;
        \\end{tikzpicture
        """
        self.connectome += ["sharp corners"]
        return self

    def draw_circle(self, radius: Scalar, scale: t.Union[int, float] = None) -> "Path":
        """
        Section 14.6 The Circle and Ellipse Operations
        \path ... circle[〈options〉] ...;
        """
        _ops = [f"radius={radius}"]
        if scale is not None:
            _ops += [f"scale={scale}"]
        self.connectome += [f"circle [" + ", ".join(_ops) + "]"]
        return self

    def draw_ellipse(
        self,
        x_radius: Scalar, y_radius: Scalar,
        scale: t.Union[int, float] = None, rotate: t.Union[int, float] = None
    ) -> "Path":
        """
        Section 14.6 The Circle and Ellipse Operations
        \\path ... ellipse[〈options〉] ...;
        """
        _ops = [f"x radius={x_radius}", f"y radius={y_radius}", ]
        if scale is not None:
            _ops += [f"scale={scale}"]
        if rotate is not None:
            _ops += [f"rotate={rotate}"]
        self.connectome += [f"circle [" + ", ".join(_ops) + "]"]
        return self

    def draw_arc(
        self,
        radius: Scalar = None,
        x_radius: Scalar = None, y_radius: Scalar = None,
        start_angle: t.Union[int, float] = None,
        end_angle: t.Union[int, float] = None,
        delta_angle: t.Union[int, float] = None,
    ) -> "Path":
        """
        Section 14.7 The Arc Operation
        \\path ... arc[〈options〉] ...;
        """
        # validations
        if radius is not None:
            if x_radius is not None or y_radius is not None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "If radius is specified do not specify x_radius and(or) y_radius"
                    ]
                )
        else:
            if x_radius is None or y_radius is None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Please specify x_radius and y_radius or else specify radius"
                    ]
                )
        if start_angle is None:
            raise e.validation.NotAllowed(msgs=["Please specify start_angle"])
        if not (end_angle is None ^ delta_angle is None):
            raise e.validation.NotAllowed(msgs=["Specify one of end_angle or delta_angle"])

        # bake options
        _ops = []
        if radius is not None:
            _ops += [f"radius={radius}"]
        if x_radius is not None:
            _ops += [f"x radius={x_radius}"]
        if y_radius is not None:
            _ops += [f"y radius={y_radius}"]
        if start_angle is not None:
            _ops += [f"start angle={start_angle}"]
        if end_angle is not None:
            _ops += [f"end angle={end_angle}"]
        if delta_angle is not None:
            _ops += [f"delta angle={delta_angle}"]

        # make connectome
        self.connectome += [f"arc [{','.join(_ops)}]"]
        return self

    def draw_grid(
        self,
        corner: t.Union[Point, _Node],
        step: t.Union[int, float, Scalar, Point] = None,
        xstep: t.Union[int, float, Scalar] = None,
        ystep: t.Union[int, float, Scalar] = None,
        rotate: t.Union[int, float] = None,
    ) -> "Path":
        """
        Section 14.8 The Grid Operation
        \path ... grid[〈options〉]〈corner or cycle〉 ...;

        todo: add support for help lines
          \tikz \draw[help lines](0,0) grid (3,3);
        """
        if step is not None:
            if xstep is not None:
                raise e.validation.NotAllowed(msgs=["Please do not use xstep as you are using step"])
            if ystep is not None:
                raise e.validation.NotAllowed(msgs=["Please do not use ystep as you are using step"])
        if isinstance(corner, _Node):
            corner = f"({corner.name})"
        _options = []
        if step is not None:
            _options.append(f"step={step}")
        if xstep is not None:
            _options.append(f"xstep={xstep}")
        if ystep is not None:
            _options.append(f"ystep={ystep}")
        if rotate is not None:
            _options.append(f"rotate={rotate}")

        self.connectome += [f"grid [{','.join(_options)}] {corner}"]
        return self

    def draw_parabola(
        self,
        to: t.Union[Point, _Node],
        bend: t.Union[Point, _Node] = None,
        bend_pos: float = None,
        height: Scalar = None, bend_at_start: bool = False, bend_at_end: bool = False
    ) -> "Path":
        """
        Section 14.9 The Parabola operation
        \path ... parabola[〈options〉]bend〈bend coordinate〉〈coordinate or cycle〉 ...;
        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        if isinstance(bend, _Node):
            bend = f"({bend.name})"
        _options = []
        if bend_pos is not None:
            _options.append(f"bend pos={bend_pos}")
        if height is not None:
            _options.append(f"parabola height={height}")
        if bend_at_start:
            _options.append("bend at start")
        if bend_at_end:
            _options.append("bend at end")

        _p = "parabola"
        if bool(_options):
            _p += "[" + ",".join(_options) + "]"

        if bend is not None:
            _p += f"bend{bend}"

        _p += f"{to}"

        self.connectome += [_p]

        return self

    def draw_sin(self, to: t.Union[Point, _Node]) -> "Path":
        """
        Section 14.10 The Sine and Cosine Operation
        \path ... sin〈coordinate or cycle〉 ...;

        Note that there is no way to (conveniently) draw an interval on a sine
        or cosine curve whose end points are not multiples of π/2.
        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        self.connectome += [f"sin {to}"]
        return self

    def draw_cos(self, to: Point) -> "Path":
        """
        Section 14.10 The Sine and Cosine Operation
        \path ... cos〈coordinate or cycle〉 ...;

        Note that there is no way to (conveniently) draw an interval on a sine
        or cosine curve whose end points are not multiples of π/2.
        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        self.connectome += [f"cos {to}"]
        return self

    def draw_svg(self):
        """
        Section 14.11 The SVG Operation
        """
        # todo: TBD later
        raise NotImplemented()

    def draw_plot(
        self,
        x: t.List[t.Union[int, float]], y: t.List[t.Union[int, float]],
        width: Scalar, height: Scalar,
        x_min: t.Union[int, float] = None, x_max: t.Union[int, float] = None,
        y_min: t.Union[int, float] = None, y_max: t.Union[int, float] = None,
        relative: t.Literal['+', '++', ''] = '',
    ) -> "Path":
        """
        Section 14.12 The Plot Operations ... tells checking section 22
        Section 22 Plots of Functions

        \path ... --plot〈further arguments〉 ...;
        >> --plot[〈local options〉]coordinates{〈coordinate 1〉〈coordinate 2〉...〈coordinate n〉}
           We are using this one
        >> --plot[〈local options〉]file{〈filename〉}
           Can be done by python i.e. we will read file or get data using python
           So no need to implement this
        >> --plot[〈local options〉]〈coordinate expression〉
           Need to know PGF mathematical engine .... still we can do this in Python
        >> --plot[〈local options〉]function{〈gnuplot formula〉}
           todo: TBD later in draw_plot_fn
           This is useful to draw some fix functions like horizontal vertical
           threshold lines which are finite


        Note that we will have `tikz.pgfplots` for having more complex plots.
        This plot is aimed at using plots inside tikz figure. So do expect this
        function to do much as tikz is not plotting program and in complex cases
        will call gnuplot ...

        But in many cases using this is good as it will melt well with entire tex
        documents like font, size, formula in labels ...

        todo: expand later for now we will have very simple plot with coordinates
          For this refer Section 16 and implement it ...
          Also note that `tikz.pgfplots` is always there so we do not expect more
          things from this method ...
        """

        # ----------------------------------------- 01
        # compute vars
        if y_min is None:
            y_min = min(y)
        if y_max is None:
            y_max = max(y)
        if x_min is None:
            x_min = min(x)
        if x_max is None:
            x_max = max(x)
        y_min = float(y_min)
        y_max = float(y_max)
        x_min = float(x_min)
        x_max = float(x_max)

        # ----------------------------------------- 02
        # transform x and y ... so that everything is between 0 and 1
        x = (np.asarray(x)-x_min)/x_max
        y = (np.asarray(y)-y_min)/y_max

        # ----------------------------------------- 03
        # scale it to given height and width
        if width.unit != height.unit:
            raise e.validation.NotAllowed(
                msgs=["Was expecting the unit of height and width to be same"]
            )
        _unit = width.unit
        x *= width.value
        y *= height.value
        x = x.astype(np.float32)
        y = y.astype(np.float32)

        # ----------------------------------------- 04
        # make coordinates list
        _points = []
        for _x, _y in zip(x, y):
            _points.append(
                str(Point2D(Scalar(_x, _unit), Scalar(_y, _unit), relative=relative))
            )

        # ----------------------------------------- 06
        # add to connectome
        self.connectome += [f"plot coordinates {{{' '.join(_points)}}}"]

        # ----------------------------------------- 07
        # return
        return self

    def draw_plot_fn(
        self,
        fn: str,
    ) -> "Path":
        """

        Section 14.12 The Plot Operations ... tells checking section 22
        Section 22 Plots of Functions
        Section 22.6 Plotting a Function Using Gnuplot

        \path ... --plot〈further arguments〉 ...;
        >> --plot[〈local options〉]coordinates{〈coordinate 1〉〈coordinate 2〉...〈coordinate n〉}
           We are using this one
        >> --plot[〈local options〉]file{〈filename〉}
           Can be done by python i.e. we will read file or get data using python
           So no need to implement this
        >> --plot[〈local options〉]〈coordinate expression〉
           Need to know PGF mathematical engine .... still we can do this in Python
        >> --plot[〈local options〉]function{〈gnuplot formula〉}
           todo: TBD later in draw_plot_fn
           This is useful to draw some fix functions like horizontal vertical
           threshold lines which are finite

        """
        raise NotImplementedError()

    def to(
        self,
        to: t.Union[Point, _Node],
        *,
        out_: t.Union[int, float] = None,
        in_: t.Union[int, float] = None,
        relative: bool = False,
        bend_left: t.Union[int, float] = None,
        bend_right: t.Union[int, float] = None,
        bend_angle: t.Union[int, float] = None,
        looseness: t.Union[int, float] = None,
        out_looseness: t.Union[int, float] = None,
        in_looseness: t.Union[int, float] = None,
        min_distance: Scalar = None,
        max_distance: Scalar = None,
        out_min_distance: Scalar = None,
        out_max_distance: Scalar = None,
        in_min_distance: Scalar = None,
        in_max_distance: Scalar = None,
        distance: Scalar = None,
        out_distance: Scalar = None,
        in_distance: Scalar = None,
        out_control: Point = None,
        in_control: Point = None,
        controls: t.Tuple[Point, Point] = None,
        loop: bool = False,
        loop_above: bool = False,
        loop_below: bool = False,
        loop_left: bool = False,
        loop_right: bool = False,
        nodes: t.List[Node] = None,
    ) -> "Path":
        """
        Section 14.13 The To Path operation (notTo Path Library)
        \path ... to[〈options〉] 〈nodes〉〈 coordinate or cycle〉 ...;

        Section 74: To Path Library
        This is library .... crate class ToPathOptions for this as it can be
          applied to both to and edge operation

        The to operation is used to add a user-defined path from the previous
        coordinate to the following coordinate. When you write (a) to (b), a
        straight line is added from a to b, exactly as if you had written
        (a) -- (b). However, if you write (a) to [out=135,in=45] (b) a curve
        is added to the path, which leaves at an angle of 135◦ at a and
        arrives at an angle of 45◦ at b. This is because the options in and
        out trigger a special path to be used instead of the straight line.

        The above para can be done with `line_to()` and `curve_to()` methods.

        """
        if isinstance(to, _Node):
            to = f"({to.name})"
        _t = []
        if out_ is not None:
            _t.append(f"out={out_}")
        if in_ is not None:
            _t.append(f"in={in_}")
        if relative:
            _t.append("relative")
        if bend_left is not None:
            _t.append(f"bend left={bend_left}")
        if bend_right is not None:
            _t.append(f"bend right={bend_right}")
        if bend_angle is not None:
            _t.append(f"bend angle={bend_angle}")
        if looseness is not None:
            _t.append(f"looseness={looseness}")
        if out_looseness is not None:
            _t.append(f"out looseness={out_looseness}")
        if in_looseness is not None:
            _t.append(f"in looseness={in_looseness}")
        if min_distance is not None:
            _t.append(f"min distance={min_distance}")
        if max_distance is not None:
            _t.append(f"max distance={max_distance}")
        if out_min_distance is not None:
            _t.append(f"out min distance={out_min_distance}")
        if out_max_distance is not None:
            _t.append(f"out max distance={out_max_distance}")
        if in_min_distance is not None:
            _t.append(f"in min distance={in_min_distance}")
        if in_max_distance is not None:
            _t.append(f"in max distance={in_max_distance}")
        if distance is not None:
            _t.append(f"distance={distance}")
        if out_distance is not None:
            _t.append(f"out distance={out_distance}")
        if in_distance is not None:
            _t.append(f"in distance={in_distance}")
        if out_control is not None:
            _t.append(f"out control={out_control}")
        if in_control is not None:
            _t.append(f"in control={in_control}")
        if controls is not None:
            _t.append(f"controls={controls[0]} and {controls[1]}")
        if loop:
            _t.append("loop")
        if loop_above:
            _t.append("loop above")
        if loop_below:
            _t.append("loop below")
        if loop_left:
            _t.append("loop left")
        if loop_right:
            _t.append("loop right")

        # check if loop related and test/modify `to` if None
        _is_loop_related = loop or loop_above or loop_below or loop_left or loop_right
        if to is None:
            if _is_loop_related:
                # None is allowed for loops
                to = "()"
            else:
                # `to` is mandatory when not loop
                raise e.code.CodingError(
                    msgs=[
                        f"The `to` kwarg is mandatory when not using for loop"
                    ]
                )

        # select op
        _op = "to "

        # expand connectome
        _t_str = "[" + ",".join(_t) + "]"
        if bool(nodes):
            self.connectome += [_op + _t_str, nodes, to]
        else:
            self.connectome += [_op + _t_str, to]

        # return
        return self

    def edge(
        self,
        to: t.Union[Point, str],
        # *,
    ):
        """
        14.17 The Node and Edge Operations
        17 Nodes and Edges

        The node operation adds a so-called node to a path. This operation is
        special in the following sense: It does not change the current path
        in any way. In other words, this operation is not really a path
        operation, but has an effect that is “external” to the path.

        The edge operation has similar effect in that it adds something after
        the main path has been drawn. However, it works like the to operation,
        that is, it adds a to path to the picture after the main path has been
        drawn. Since these operations are quite complex, they are described
        in the separate Section 17.


        \path ... edge[〈options〉] 〈nodes〉 (〈coordinate〉)

        Read this answer to understand why edge is different from `to()`
        https://tex.stackexchange.com/questions/314301/tikz-when-will-i-need-to-use-edge-and-how-does-it-differ-from-the-conventional/314306#314306

        Note that this only draws edges with tips at end but does not move the path like `to()`

        Section 17.12: Connecting Nodes: Using the Edge Operation
        The edge operation works like a to operation that is added after the
        main path has been drawn, much like a node is added after the main
        path has been drawn. This allows each edge to have a different
        appearance. As the node operation, an edge temporarily suspends the
        construction of the current path and a new path p is constructed.
        This new path p will be drawn after the main path has been drawn. Note
        that p can be totally different from the main path with respect to
        its options. Also note that if there are several edge and/or node
        operations in the main path, each creates its own path(s) and they
        are drawn in the order that they are encountered on the main path.

        """
        ...

    def loop(
        self,
        to: t.Union[Point, str],
        # *,
    ):
        """
        We will have special method instead of using `to()` or `edge()` to draw loops on our nodes
        This is just for convenience
        """
        ...


@dataclasses.dataclass
class TikZ(LaTeX):

    nodes: t.List[Node] = dataclasses.field(default_factory=list)

    @property
    @util.CacheResult
    def paths(self) -> t.List[Path]:
        return []

    @property
    def open_clause(self) -> str:
        _ret = []
        for _k, _s in self.styles.items():
            _ret.append(
                f"\\tikzstyle{{{_k}}}=[{_s}]"
            )
        _ret.append("\\begin{tikzpicture}")

        # process all nodes and add them at start
        for _n in self.nodes:
            _ret.append("\\" + str(_n) + " ;")

        # return
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = ["\\end{tikzpicture}"]
        return "\n".join(_ret)

    @property
    @util.CacheResult
    def styles(self) -> t.Dict[str, Style]:
        """
        Refer section 3.5 Using Styles
        """
        return {}

    def __str__(self):
        if bool(self._items):
            # todo: address this issue later
            raise e.code.CodingError(
                msgs=["Do not call this twice as self.items will be populated again"]
            )

        # keep reference for _tikz ...
        # __str__ is like build, so we do these assignments here
        for _p in self.paths:
            # LaTeX parent class does not understand Path it only understands str or
            # subclasses of LaTeX
            self._items.append(str(_p))

        # return
        return super().__str__()

    def init_validate(self):
        # call super
        super().init_validate()

        # more validations
        if self.label is not None:
            raise e.validation.NotAllowed(
                msgs=["label field is not usable with TikZ so do not set it"]
            )

        # check if id provided .... and also detect if duplicate
        _n_ids = []
        for _n in self.nodes:
            _n_id = _n.name
            if _n_id is None:
                raise e.code.NotAllowed(
                    msgs=["Please supply id for node as this will be declared globally to be used by TikZ",
                          "Only nodes that are declared on path or as pin or label can be used without id"]
                )
            e.validation.ShouldNotBeOneOf(
                value=_n_id, values=_n_ids,
                msgs=["The node id is already taken"]
            ).raise_if_failed()
            _n_ids.append(_n_id)
            # this is because node can have pin and labels which also happen to be special nodes
            _pins_or_labels = []
            if bool(_n.pins):
                _pins_or_labels.extend(_n.pins)
            if bool(_n.labels):
                _pins_or_labels.extend(_n.labels)
            for _p_or_l in _pins_or_labels:
                _p_or_l_id = _p_or_l.name
                if _p_or_l_id is None:
                    continue
                e.validation.ShouldNotBeOneOf(
                    value=_p_or_l_id, values=_n_ids,
                    msgs=["The pin/label node id is already taken"]
                ).raise_if_failed()
                _n_ids.append(_p_or_l_id)

    def add_paths(self, paths: t.List[Path]) -> "TikZ":
        for _p in paths:
            self.add_path(_p)
        return self

    def add_path(self, path: Path) -> "TikZ":
        # when style key provided check if it is registered ...
        if isinstance(path.style, str):
            e.validation.ShouldBeOneOf(
                value=path.style, values=list(self.styles.keys()),
                msgs=[f"Style {path.style} is not registered with tikz"]
            ).raise_if_failed()

        # if tikz not present provide it
        # noinspection PyProtectedMember
        if path._tikz is None:
            path._tikz = self
        else:
            # noinspection PyProtectedMember
            if id(path._tikz) != id(self):
                raise e.code.CodingError(
                    msgs=["_tikz was already set ... "
                          "and path may be from different tikz picture"]
                )

        # add to items
        self.paths.append(path)

        # return self for chaining
        return self

    def register_style(self, key: str, style: Style):
        if not key.startswith("s_"):
            raise e.validation.NotAllowed(
                msgs=["Style should start with s_"]
            )
        if key not in self.styles:
            self.styles[key] = style
        else:
            raise e.validation.NotAllowed(
                msgs=[f"Style with key {key} is already registered ..."]
            )

    def show_debug_grid(
        self,
        width: Scalar = Scalar(1, 'textwidth'),
        height: Scalar = Scalar(1.5, 'textwidth'),
        step: Scalar = Scalar((1-0.05)/20, 'textwidth'),
        color: Color = Color.yellow,
    ) -> "TikZ":
        _path = Path(
            style=Style(
                draw=DrawOptions(
                    color=color,
                )
            )
        ).move_to(
            Point2D(Scalar(0, 'cm'), Scalar(0, 'cm'))
        ).draw_grid(
            corner=Point2D(width, height),
            step=step,
        ).move_to(
            Point2D(Scalar(0, 'cm'), Scalar(0, 'cm'))
        )
        self.add_path(_path)

        return self

    def get_current_bounding_box(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # bounding box of the current picture
        _node = Node(name="current bounding box")
        # noinspection PyProtectedMember
        _node._tikz = self
        return _node

    def get_current_path_bounding_box(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # bounding box of the current path
        _node = Node(name="current path bounding box")
        # noinspection PyProtectedMember
        _node._tikz = self
        return _node

    def get_current_page(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # ...
        _node = Node(name="current page")
        # noinspection PyProtectedMember
        _node._tikz = self
        return _node

    def get_last_node(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # todo: not sure how to get last node ... explore
        #    \\tikzlastnode ... check section 13.14 Executing Code After Nodes
        # last_node = Node(id="first node")
