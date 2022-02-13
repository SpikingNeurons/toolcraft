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
    

class NodeStyle(t.NamedTuple):
    shape: t.Literal['circle', 'ellipse', 'rectangle'] = None
    double: bool = False
    rounded_corners: bool = False
    
    def __str__(self):
        _options = []
        if self.shape is not None:
            _options.append(f"shape={self.shape}")
        if self.double:
            _options.append("double")
        if self.rounded_corners:
            _options.append("rounded corners")
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
        # Note that if Anchor then __str__ can handle if using non-intuitive anchors
        return f"({self.node.id}.{self.anchor})"


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
            if str(self.draw).find("fill") == -1:
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
class TikZ(LaTeX):
    @property
    def preambles(self) -> t.List[str]:
        return ["\\usepackage{tikz}"] + super().preambles

    @property
    def open_clause(self) -> str:
        return "% >> start tikz picture \n\\begin{tikzpicture}"

    @property
    def close_clause(self) -> str:
        return "% >> end tikz picture \n\\end{tikzpicture}"

    def path(
        self,
        path_items: t.List[t.Union[
            Point2D, Point3D, PointPolar
        ]],
        draw: Color = None,
        fill: Color = None,
        # clip: ... = None,
        # shade: ... = None,
        draw_intensity: int = None,
        fill_intensity: int = None,
        thickness: Thickness = None,
        opacity: int = None,
        fill_opacity: int = None,
        draw_opacity: int = None,
    ) -> "TikZ":
        """
        Section 8.3: Actions on Paths
        https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf

        A path is just a series of straight and curved lines, but it is not yet
        specified what should happen with it.
        One can
          + draw a path,
          + fill a path,
          + shade it,
          + clip it, or
          + do any combination of these.

        Drawing (also known as stroking) can be thought of as taking a pen of a
        certain thickness and moving it along the path, thereby drawing on the canvas.

        Filling means that the interior of the path is filled with a uniform color.
        Obviously, filling makes sense only for closed paths and a path is
        automatically closed prior to filling, if necessary.

        NOTE:
            We simplify our code and use only path as generic method. We don't need
            to support abbreviations like \\draw, \\fill, \\filldraw
            Also \\node is abbreviation for \\path node
            Also \\coordinate is abbreviation for \\path coordinate

        """
        # -------------------------------------------------------- 01
        # validation
        if draw_intensity is not None and draw is None:
            raise e.validation.NotAllowed(
                msgs=[
                    "If you supplied draw_intensity then you must also supply draw"
                ]
            )
        if fill_intensity is not None and fill is None:
            raise e.validation.NotAllowed(
                msgs=[
                    "If you supplied fill_intensity then you must also supply fill"
                ]
            )
        if fill_opacity is not None or draw_opacity is not None:
            if opacity is not None:
                raise e.validation.NotAllowed(
                    msgs=[
                        "If you are supplying either of `fill_opacity` or(and) "
                        "`draw_opacity` then you need not supply `opacity` ..."
                    ]
                )
        # -------------------------------------------------------- 02
        # determine command
        if fill is not None:
            if draw is None:
                _cmd = "\\fill"
            else:
                _cmd = "\\filldraw"
        else:
            _cmd = "\\draw"
        # -------------------------------------------------------- 03
        # make options str
        _options = []
        if fill is not None:
            _fill = f"fill={fill.value}"
            if fill_intensity is not None:
                _fill += f"!{fill_intensity}"
            _options.append(_fill)
        if draw is not None:
            _draw = f"draw={draw.value}"
            if draw_intensity is not None:
                _draw += f"!{draw_intensity}"
            _options.append(_draw)
        if thickness is not None:
            _options.append(thickness.value)
        _options = "[" + ", ".join(_options) + "]"
        # -------------------------------------------------------- 04
        _draw_item_cmd = f"{_cmd}{_options} {draw_item};%"
        self.items.append(_draw_item_cmd)
        # -------------------------------------------------------- 05
        # return self
        return self

    def draw_circle(
        self, x: t.Union[int, float], y: t.Union[int, float],
        radius: t.Union[int, float],
        draw: Color = None, draw_intensity: t.Union[int, float] = None,
        fill: Color = None, fill_intensity: t.Union[int, float] = None,
        thickness: Thickness = None,
        opacity: t.Union[int, float] = None,
        fill_opacity: t.Union[int, float] = None,
        draw_opacity: t.Union[int, float] = None,
    ) -> "TikZ":
        return self.draw(
            draw_item=f"({x}, {y}) circle ({radius}pt)",
            draw=draw, draw_intensity=draw_intensity,
            fill=fill, fill_intensity=fill_intensity,
            thickness=thickness,
            opacity=opacity, fill_opacity=fill_opacity, draw_opacity=draw_opacity
        )

    def draw_line(
        self,
        cycle: bool = False,
        draw: Color = None, draw_intensity: t.Union[int, float] = None,
        fill: Color = None, fill_intensity: t.Union[int, float] = None,
        thickness: Thickness = None,
        opacity: t.Union[int, float] = None,
        fill_opacity: t.Union[int, float] = None,
        draw_opacity: t.Union[int, float] = None,
    ) -> "TikZ":
        return self.draw(
            draw_item=f"({x}, {y}) circle ({radius}pt)",
            draw=draw, draw_intensity=draw_intensity,
            fill=fill, fill_intensity=fill_intensity,
            thickness=thickness,
            opacity=opacity, fill_opacity=fill_opacity, draw_opacity=draw_opacity
        )
