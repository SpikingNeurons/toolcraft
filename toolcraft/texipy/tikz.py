"""
Supporting tutorial: https://www.overleaf.com/learn/latex/TikZ_package

More official tutorial: https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf
We can convert this entirely ...
"""

import dataclasses
import typing as t
import abc
import enum

from .. import error as e
from .__base__ import LaTeX, Color, Thickness, Font, Scalar


class Shape(enum.Enum):
    rectangle = "rectangle"
    circle = "circle"
    ellipse = "ellipse"
    circle_split = "circle split"
    forbidden_sign = "forbidden sign"
    diamond = "diamond"
    cross_out = "cross out"
    strike_out = "strike out"
    regular_polygon = "regular polygon"
    star = "star"

    def __str__(self):
        return self.__call__()

    def __call__(
        self,
        regular_polygon_sides: int = None,
        star_points: int = None, star_point_ratio: float = None,
    ):
        # deal with regular_polygon
        if self is self.regular_polygon:
            if regular_polygon_sides is not None:
                return f"regular polygon,regular polygon sides={regular_polygon_sides}"

        # deal with star
        if self is self.star:
            if star_points is not None or star_point_ratio is not None:
                _ret = ["star"]
                if star_points is not None:
                    _ret.append(f"star points={star_points}")
                if star_point_ratio is not None:
                    _ret.append(f"star point ratio={star_point_ratio}")
                return ",".join(_ret)

        # return
        return self.value


class NodeStyle(t.NamedTuple):
    shape: t.Union[str, Shape] = None
    inner_sep: Scalar = None
    inner_xsep: Scalar = None
    inner_ysep: Scalar = None
    outer_sep: Scalar = None
    outer_xsep: Scalar = None
    outer_ysep: Scalar = None
    minimum_height: Scalar = None
    minimum_width: Scalar = None
    minimum_size: Scalar = None
    aspect: t.Union[int, float] = None
    double: bool = False
    rounded_corners: bool = False
    thickness: t.Union[Thickness, Scalar] = None

    def __str__(self):
        _options = []
        if self.shape is not None:
            _options.append(f"shape={self.shape}")

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

        if self.aspect is not None:
            _options.append(f"aspect={self.aspect}")

        if self.double:
            _options.append("double")
        if self.rounded_corners:
            _options.append("rounded corners")

        if self.thickness is not None:
            if isinstance(self.thickness, Thickness):
                _options.append(str(self.thickness))
            else:
                _options.append(f"line width={self.thickness}")

        return ",".join(_options)


class Transform(t.NamedTuple):

    rotate: t.Union[int, float] = None
    shift: 'Point' = None

    def __str__(self):
        _options = []
        if self.shift is not None:
            _options.append(f"shift={{{self.shift}}}")
        if self.rotate is not None:
            _options.append(f"rotate={self.rotate}")
        return ",".join(_options)


class TextStyle(t.NamedTuple):
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
            # A color= option will immediately override this option ...
            # todo: figure out later what is color option
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
    # (special anchor)
    angle = enum.auto()

    # (non-intuitive anchors)
    # please refer section 49.6 to see what anchors are available on node ...
    # this also varies based on shape used (todo: add checks later)
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

    # (intuitive anchors)
    above = "above"
    above_left = "above left"
    above_right = "above right"
    below = "below"
    below_left = "below left"
    below_right = "below right"
    left = "left"
    right = "right"

    def __str__(self) -> str:
        return self.__call__()

    def __call__(
        self,
        node: "Node" = None, offset: Scalar = None,
        angle: t.Union[int, float] = None,
    ) -> str:
        """
        NOTE: angle kwarg can be only used when angle anchor is used

        For non-intuitive anchors node and offset must not be used and for getting
        offset behaviour maybe use shift field of parent Node ...

        When node is supplied we will use `of` keyword

        If `offset` is supplied
          If node is supplied will be used as `node_distance`
            [above of=<node>, node distance=<offset>]
          Else will be used as above=<offset>
        """

        # ----------------------------------------------------- 01
        # if angle anchor
        if self is self.angle:
            # angle must be provided
            if angle is None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Please supply kwarg `angle` ... "
                        "as you are using angle anchor"
                    ]
                )
            # node and offset should not be supplied
            if node is not None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "When using angle anchor you cannot use "
                        "`node` kwarg"
                    ]
                )
            if offset is not None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "When using angle anchor you cannot use "
                        "`offset` kwarg"
                    ]
                )
            # return
            return f"anchor={angle}"
        # if we reach here then it is not angle error so raise error if kwarg
        # angle is supplied
        if angle is not None:
            raise e.validation.NotAllowed(
                msgs=[
                    "Please do not supply kwarg `angle` ... "
                    "as you are not using angle anchor"
                ]
            )

        # ----------------------------------------------------- 02
        # for intuitive anchors
        if self in [
            self.left, self.right,
            self.above, self.above_left, self.above_right,
            self.below, self.below_left, self.below_right,
        ]:
            # if `node` is not provided then do not use `of` behaviour and use kwarg
            # `offset` as `offset`
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

        # ----------------------------------------------------- 03
        # rest all we assume are non-intuitive anchors
        # node and offset should not be supplied
        if node is not None:
            raise e.validation.NotAllowed(
                msgs=[
                    "When using non-intuitive anchors you cannot use "
                    "`node` kwarg"
                ]
            )
        if offset is not None:
            raise e.validation.NotAllowed(
                msgs=[
                    "When using non-intuitive anchors you cannot use "
                    "`offset` kwarg"
                ]
            )
        # return str repr
        return f"anchor={self.value}"
    

class Point(abc.ABC):
    """
    Point are like coordinate that are lightweight nodes without shape and `at` part
    can be missed as it infers it
    \\path ... coordinate[⟨options⟩](⟨name⟩)at(⟨coordinate⟩) ...;

    This is same as
    node[shape=coordinate][⟨options⟩](⟨name⟩)at(⟨coordinate⟩){},
    """

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


class Point2D(t.NamedTuple, Point):
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


class Point3D(t.NamedTuple, Point):
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


class PointPolar(t.NamedTuple, Point):
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


class PointOnNode(t.NamedTuple, Point):
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
    node: "Node" = None
    anchor: t.Union[int, float, Anchor] = None

    def __str__(self):
        _ret = "("

        if self.node is None:
            _ret += "first node"
            raise e.code.CodingError(
                msgs=[f"We have not yet figured this out ... "
                      f"implement check and then use"]
            )
        else:
            if self.node.id is None:
                e.validation.NotAllowed(
                    msgs=[
                        "Cannot provide point on this node as it does not have "
                        "`id` specified ..."
                    ]
                )
            _ret += f"{self.node.id}"

        if self.anchor is not None:
            # Note that if Anchor then __str__ can handle
            # only if using non-intuitive anchors
            _ret += f".{self.anchor}"

        return _ret + ")"


class Node(t.NamedTuple):
    """

    Understanding points on Node
      The properties/methods that return `PointOnNode` please refer section 49.6

    The LaTeX syntax:
      \\path ... node[⟨options⟩](⟨name⟩)at(⟨coordinate⟩){⟨text⟩} ...;

    todo: support multi-part nodes (see section 13.3)
    """
    # id
    id: str = None

    # refer section 13.4: Options for the Text in Nodes
    text_to_display: str = None
    
    # style
    node_style: NodeStyle = None
    text_style: TextStyle = None

    # transform
    transform: Transform = None

    draw: t.Union[str, Color] = None
    fill: t.Union[str, Color] = None

    # Refer: 13.5: Placing Nodes Using Anchors
    # with this field we address all below latex node options
    #  anchor, above, above left, left ... above of, above left of, left of ...
    # this will only anchor current node at specific node.anchor (i.e. PointOnNode)...
    # but for generic coordinates use @ operator ... which uses special
    # `at` latex keyword
    anchor: t.Union[str, Anchor] = None

    def __matmul__(self, other: Point) -> str:
        """
        We use new @ operator for `at` tikz keyword
        """
        _node_str = str(self)
        _brace_index = _node_str.rfind("{")
        return _node_str[:_brace_index] + f"at {other} " + _node_str[_brace_index:]

    def __str__(self):
        """
        The LaTeX syntax:
          \\path ... node[⟨options⟩](⟨name⟩)at(⟨coordinate⟩){⟨text⟩} ...;
        """
        # the token to return
        _ret = "node"

        # add id if specified
        if self.id is not None:
            _ret += f"({self.id})"
        _ret += " "

        # make options
        _options = []
        if self.draw is not None:
            if str(self.draw).find("draw") == -1:
                e.validation.NotAllowed(
                    msgs=[
                        f"Use method {Color.for_draw} to assign draw color ..."
                    ]
                )
            _options.append(str(self.draw))
        if self.fill is not None:
            if str(self.fill).find("fill") == -1:
                e.validation.NotAllowed(
                    msgs=[
                        f"Use method {Color.for_fill} to assign fill color ..."
                    ]
                )
            _options.append(str(self.fill))
        if self.transform is not None:
            _options.append(str(self.transform))
        if self.node_style is not None:
            _options.append(str(self.node_style))
        if self.text_style is not None:
            _options.append(str(self.text_style))
        if self.anchor is not None:
            _options.append(str(self.anchor))
        _ret += "[" + ",".join(_options) + "] "

        # finally, add text value if supplied
        if self.text_to_display is not None:
            _ret += "{" + self.text_to_display + "}"

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

    def point_at_angle(self, angle: t.Union[int, float]) -> PointOnNode:
        return PointOnNode(node=self, anchor=angle)


@dataclasses.dataclass
class Path:
    """
    Most important component for TikZ class.
    Class can have
      Point (i.e. tikz coordinate)
      Node (i.e. tikz node)

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

    # actions
    draw: t.Union[str, Color] = None
    fill: t.Union[str, Color] = None
    # clip
    # shade

    # some options for path
    thickness: t.Union[Thickness, Scalar] = None

    # cycle
    cycle: bool = False

    def __post_init__(self):
        # container to save all segments of path
        self.connectome = []

    def __str__(self):
        # ---------------------------------------------------------- 01
        # return str
        _ret = "path"

        # ---------------------------------------------------------- 02
        # make options
        _options = []
        # ---------------------------------------------------------- 02.01
        if self.draw is not None:
            if str(self.draw).find("draw") == -1:
                e.validation.NotAllowed(
                    msgs=[
                        f"Use method {Color.for_draw} to assign draw color ..."
                    ]
                )
            _options.append(str(self.draw))
        # ---------------------------------------------------------- 02.02
        if self.fill is not None:
            if str(self.fill).find("fill") == -1:
                e.validation.NotAllowed(
                    msgs=[
                        f"Use method {Color.for_fill} to assign fill color ..."
                    ]
                )
            _options.append(str(self.fill))
        # ---------------------------------------------------------- 02.03
        if self.thickness is not None:
            if isinstance(self.thickness, Thickness):
                _options.append(str(self.thickness))
            else:
                _options.append(f"line width={self.thickness}")
        # ---------------------------------------------------------- 02.04
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
        return _ret

    def connect(
        self, item: t.Union[Point2D, Point3D, PointPolar, PointOnNode, Node]
    ) -> 'Path':
        self.connectome += ['--', item]
        return self

    # noinspection PyPep8Naming
    def connect_HV(
        self, item: t.Union[Point2D, Point3D, PointPolar, PointOnNode, Node]
    ) -> 'Path':
        self.connectome += ['-|', item]
        return self

    # noinspection PyPep8Naming
    def connect_VH(
        self, item: t.Union[Point2D, Point3D, PointPolar, PointOnNode, Node]
    ) -> 'Path':
        self.connectome += ['|-', item]
        return self

    def connect_hidden(
        self, item: t.Union[Point2D, Point3D, PointPolar, PointOnNode, Node]
    ) -> 'Path':
        self.connectome += [' ', item]
        return self


@dataclasses.dataclass
class TikZ(LaTeX):
    @property
    def preambles(self) -> t.List[str]:
        return [
            "\\usepackage{tikz}",
            "\\usetikzlibrary{shapes}",
            "\\usetikzlibrary{snakes}",
        ] + super().preambles

    @property
    def open_clause(self) -> str:
        return "% >> start tikz picture \n\\begin{tikzpicture}"

    @property
    def close_clause(self) -> str:
        return "% >> end tikz picture \n\\end{tikzpicture}"
