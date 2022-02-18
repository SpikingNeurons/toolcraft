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

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Font, Scalar


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

    todo: add validations to restrict some options bases on snake type ...
      As of now we allow all options but this can be restricted based on
      documentation ...
    """
    type: Snake = None
    raise_snake: Scalar = None

    segment_amplitude: Scalar = None
    segment_length: Scalar = None
    segment_aspect: t.Union[int, float] = None
    segment_angle: t.Union[int, float] = None
    segment_object_length: Scalar = None

    def __str__(self) -> str:
        _options = []

        if self.type is not None:
            _options.append(str(self.type))
        if self.raise_snake is not None:
            _options.append(str(self.raise_snake))

        if self.segment_amplitude is not None:
            _options.append(f"segment amplitude={self.segment_amplitude}")
        if self.segment_length is not None:
            _options.append(f"segment length={self.segment_length}")
        if self.segment_aspect is not None:
            _options.append(f"segment aspect={self.segment_aspect}")
        if self.segment_angle is not None:
            _options.append(f"segment angle={self.segment_angle}")
        if self.segment_object_length is not None:
            _options.append(f"segment object length={self.segment_object_length}")

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


class ArrowDef(enum.Enum):
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
    start_tips: t.Union[ArrowTip, t.List[ArrowTip]] = None
    end_tips: t.Union[ArrowTip, t.List[ArrowTip]] = None

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
    rounded_corners: bool = False

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
            _options.append(self.arrow_def)
        if self.rounded_corners:
            _options.append("rounded corners")
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
        # node and offset is only supported for intuitive anchors
        # todo: verify the above comment
        if _is_special or _is_non_intuitive:
            if node is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `node` for anchor {self}"]
                )
            if offset is not None:
                raise e.code.CodingError(
                    msgs=[f"Please so not supply kwarg `offset` for anchor {self}"]
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
                return f"anchor={angle}"
            if self is self.side:
                if side is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `side` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                return f"anchor=side {side}"
            if self is self.corner:
                if corner is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `corner` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                return f"anchor=corner {corner}"
            if self is self.inner_point:
                if inner_point is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `inner_point` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                return f"anchor=inner point {inner_point}"
            if self is self.outer_point:
                if outer_point is None:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Please specify `outer_point` kwarg as you are using "
                            f"special anchor {self}"
                        ]
                    )
                return f"anchor=outer point {outer_point}"

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
            return f"anchor={self.value}"

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
                    return f"{self.value} of={node.id}"
                else:
                    return f"{self.value} of={node.id}, node distance={offset}"

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

    def shift(
            self,
            x: Scalar = Scalar(0),
            y: Scalar = Scalar(0),
            z: Scalar = Scalar(0),
    ) -> str:
        _str = str(self)

        _first_brace_index = _str.find("(")

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
    relative: t.Literal['+', '++'] = ''
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
    node: "Node"
    anchor: t.Union[int, float, Anchor] = None

    def __str__(self):

        if self.node.id is None:
            e.validation.NotAllowed(
                msgs=[
                    "Cannot provide point on this node as it does not have "
                    "`id` specified ..."
                ]
            )

        _ret = f"({self.node.id}"

        # avoid using intuitive or special anchors
        if isinstance(self.anchor, Anchor):
            if self.anchor.is_special or self.anchor.is_intuitive:
                raise e.code.CodingError(
                    msgs=[]
                )

        if self.anchor is not None:
            # Note that if Anchor then __str__ can handle
            # only if using non-intuitive anchors
            _ret += f".{self.anchor}"

        return _ret + ")"


@dataclasses.dataclass
class Controls:
    """
    Set of two points specify the path
    if one is given then it uses the same for second point ...
    """
    first: Point
    second: Point = None

    def __post_init__(self):
        # set var
        # noinspection PyTypeChecker
        self._tikz = None  # type: TikZ

    def __str__(self) -> str:
        if self.second is None:
            return f".. controls {self.first} .."
        else:
            return f".. controls {self.first} and {self.second} .."


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


@dataclasses.dataclass
class Node:
    """

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

    # id
    id: str = None

    # refer section 13.4: Options for the Text in Nodes
    text_to_display: str = None

    # style
    style: t.Union[str, "Style"] = None
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

    def __matmul__(self, other: Point) -> "Node":
        """
        We use new @ operator for `at` tikz keyword
        """
        _kwargs = {
            _f.name: getattr(self, _f.name) for _f in dataclasses.fields(self)
        }
        # noinspection PyArgumentList
        _ret = self.__class__(**_kwargs)
        _ret._at = other
        return _ret

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
        # if id is provided check that there is no conflict within current tikz_context
        if self.id is not None:
            e.validation.ShouldNotBeOneOf(
                value=self.id, values=[_.id for _ in self._tikz.nodes],
                msgs=[f"Node with if {self.id} is already registered in tikz_context"]
            ).raise_if_failed()
            # Register this new node
            self._tikz.nodes.append(self)

        # -------------------------------------------------------- 03
        # the token to return
        if self._at is None:
            _ret = "node "
        else:
            _ret = f"node at {self._at} "

        # add id if specified
        if self.id is not None:
            _ret += f"({self.id})"

        # -------------------------------------------------------- 04
        # make options
        _options = []
        if self.style is not None:
            _options.append(str(self.style))
        if self.o_text is not None:
            _options.append(str(self.o_text))
        if self.o_transform is not None:
            _options.append(str(self.o_transform))
        if self.anchor is not None:
            _options.append(str(self.anchor))
        _ret += "[" + ",".join(_options) + "] "

        # -------------------------------------------------------- 05
        # finally, add text value if supplied
        if self.text_to_display is not None:
            _ret += "{" + self.text_to_display + "}"
        else:
            _ret += "{}"

        # -------------------------------------------------------- 06
        # return
        return _ret

    @property
    def center(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.center)

    @property
    def east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.east)

    @property
    def west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.west)

    @property
    def north(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north)

    @property
    def north_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north_east)

    @property
    def north_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.north_west)

    @property
    def south(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south)

    @property
    def south_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south_east)

    @property
    def south_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.south_west)

    @property
    def text(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text)

    @property
    def text_mid(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid)

    @property
    def text_mid_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid_east)

    @property
    def text_mid_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_mid_west)

    @property
    def text_base(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base)

    @property
    def text_base_east(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base_east)

    @property
    def text_base_west(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_base_west)

    @property
    def text_lower(self) -> PointOnNode:
        return PointOnNode(node=self, anchor=Anchor.text_lower)

    def point_at_angle(self, angle: t.Union[int, float]) -> PointOnNode:
        return PointOnNode(node=self, anchor=angle)

    def add_edge(self):
        ...

    def add_pin(self):
        ...

    def add_label(self):
        ...


PATH_ITEM_TYPE = t.Union[Point2D, Point3D, PointPolar, PointOnNode, Node, Controls]


@dataclasses.dataclass
class Path:
    """
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
    style: t.Union[str, "Style"] = None

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

    # cycle
    cycle: bool = False

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
        # add cycle
        if self.cycle:
            _ret += "-- cycle"

        # ---------------------------------------------------------- 05
        return _ret + ";%"

    def connect(self, item: PATH_ITEM_TYPE) -> 'Path':
        if bool(self.connectome):
            self.connectome += ['--', item]
        else:
            self.connectome += [item]
        return self

    # noinspection PyPep8Naming
    def connect_HV(self, item: PATH_ITEM_TYPE) -> 'Path':
        if bool(self.connectome):
            self.connectome += ['-|', item]
        else:
            raise e.code.CodingError(
                msgs=[f"When starting from start use {Path.connect} as the "
                      f"connectome is empty"]
            )
        return self

    # noinspection PyPep8Naming
    def connect_VH(self, item: PATH_ITEM_TYPE) -> 'Path':
        if bool(self.connectome):
            self.connectome += ['|-', item]
        else:
            raise e.code.CodingError(
                msgs=[f"When starting from start use {Path.connect} as the "
                      f"connectome is empty"]
            )
        return self

    def connect_hidden(self, item: PATH_ITEM_TYPE) -> 'Path':
        if bool(self.connectome):
            self.connectome += [' ', item]
        else:
            raise e.code.CodingError(
                msgs=[f"When starting from start use {Path.connect} as the "
                      f"connectome is empty"]
            )
        return self


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


@dataclasses.dataclass
class TikZ(LaTeX):
    caption: str = None

    @property
    @util.CacheResult
    def nodes(self) -> t.List[Node]:
        # A cached container for nodes with id ...
        return []

    @property
    def preambles(self) -> t.List[str]:
        """
        todo: move preambles to respective classes using field `tikz_context` in
          `Node` and `Path`
        """
        return [
            "\\usepackage{tikz}",
            "\\usetikzlibrary{shapes}",
            "\\usetikzlibrary{shapes.geometric}",
            "\\usetikzlibrary{shapes.symbols}",
            "\\usetikzlibrary{shapes.multipart}",
            "\\usetikzlibrary{shapes.misc}",
            "\\usetikzlibrary{snakes}",
            "\\usetikzlibrary{arrows}",
            "\\usetikzlibrary{patterns}",
            "\\usetikzlibrary{positioning}",
            "\\usetikzlibrary{calc}",
        ] + super().preambles

    @property
    def open_clause(self) -> str:
        _ret = []
        if self.caption is not None or self.label is not None:
            _ret += [
                f"% >> start figure {self.label}", "\\begin{figure}%", "\\centering%"]
        _ret.append("% >> start tikz picture")
        for _k, _s in self.styles.items():
            _ret.append(
                f"\\tikzstyle{{{_k}}}=[{_s}]"
            )
        _ret.append("\\begin{tikzpicture}%")
        return "\n".join(_ret)

    @property
    @util.CacheResult
    def paths(self) -> t.List[Path]:
        return []

    @property
    def close_clause(self) -> str:
        _ret = ["% >> end tikz picture", "\\end{tikzpicture}%"]
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}%")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}%")
        if self.caption is not None or self.label is not None:
            _ret += [f"% >> end figure: {self.label}", "\\end{figure}%"]
        return "\n".join(_ret)

    @property
    @util.CacheResult
    def styles(self) -> t.Dict[str, Style]:
        """
        Refer section 3.5 Using Styles
        """
        return {}

    def __str__(self):

        # keep reference for _tikz ...
        # __str__ is like build, so we do these assignments here
        for _p in self.paths:
            # noinspection PyProtectedMember
            if _p._tikz is None:
                _p._tikz = self
            else:
                # noinspection PyProtectedMember
                if id(_p._tikz) != id(self):
                    raise e.code.CodingError(
                        msgs=["_tikz was already set ... "
                              "and path may be from different tikz picture"]
                    )
            # LaTeX parent class does not understand Path it only understands str or
            # subclasses of LaTeX
            self.items.append(str(_p))

        # return
        return super().__str__()

    def add_path(self, path: Path) -> "TikZ":
        # when style key provided check if it is registered ...
        if isinstance(path.style, str):
            e.validation.ShouldBeOneOf(
                value=path.style, values=list(self.styles.keys()),
                msgs=[f"Style {path.style} is not registered with tikz"]
            ).raise_if_failed()

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

    def get_current_bounding_box(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # bounding box of the current picture
        return Node(id="current bounding box", tikz_context=self)

    def get_current_path_bounding_box(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # bounding box of the current path
        return Node(id="current path bounding box", tikz_context=self)

    def get_current_page(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # ...
        return Node(id="current page", tikz_context=self)

    def get_last_node(self) -> Node:
        """
        You can use these special nodes while drawing path with `TikZ.path`
        Check section 49.4 Predefined Nodes
        """
        # todo: not sure how to get last node ... explore
        #    \\tikzlastnode ... check section 13.14 Executing Code After Nodes
        # last_node = Node(id="first node")
