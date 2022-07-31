"""
Check dapr-grpc examples here
https://github.com/dapr/python-sdk/tree/master/examples

Some things to do based on this

1] invoke from client to hashable methods
  + See tutorial: rough_work/dapr/invoke
    Service invocation	Invoke service by passing bytes data
    Service invocation (advanced)	Invoke service by using custom protobuf message

"""
import datetime
import enum
import pickle
import zlib
import typing as t
from dapr.ext.grpc import InvokeMethodRequest, InvokeMethodResponse
import json
_now = datetime.datetime.now

from . import DaprMode
from .. import error as e
from .. import marshalling as m
from .. import logger

_LOGGER = logger.get_logger()


# todo: should be registered when launched via
#  `toolcraft.tools.dapr.DaprTool.command_fn` i.e.
#   when on command line `toolcraft dapr client`
# @DAPR.app.method('invoke_for_hashable_on_server')
def invoke_for_hashable_on_server(request: InvokeMethodRequest) -> bytes:
    """

    Why pickle ??
    + client is made up of python so there is no reason not to use pickle
    + With respect to pyarrow Table
      pa.serialize and pa.deserialize is deprecated as pickle protocol 5
      supports everything ... so pickling is better way for us

    todo: stream large data (we need to figure this out)
      + look for https://arrow.apache.org/docs/python/ipc.html
      + also lookout for pyarrow flight which uses grpc but also has more
        capability of reading dataframe from multiple servers

    """

    # get from request
    print("ggggggggggggggggggggggggggggggggggggggggggg")
    print(request)
    print("ggggggggggggggggggggggggggggggggggggggggggg11")
    _metadata = request.metadata
    print("ggggggggggggggggggggggggggggggggggggggggg222gg")
    raise Exception("success ... so that we can log")
    return b"receiver response ..."
    _data = json.loads(request.data)
    print("gggggggggggggggggggggggggggggggggggggggg333ggg")

    print(_data)
    print("ggggggggggggggggggggggggggggggggggggggg444gggg")

    # check if CWD set
    if DAPR.cwd is None:
        raise e.code.CodingError(
            msgs=["Dapr.CWD should be set by now ..."]
        )

    # confirm if server knows about requested hashable
    _hex_hash = _data['hex_hash']
    _hashable_yaml = DAPR.cwd / _hex_hash / ".yaml"
    if not _hashable_yaml.exists():
        if 'hashable_yaml' in _data.keys():
            _hashable_yaml.parent.mkdir(parents=True, exist_ok=True)
            _hashable_yaml.touch(exist_ok=False)
            _hashable_yaml.write_text(_data['hashable_yaml'])
        else:
            return Response(
                status=Status.NEEDS_HASHABLE_YAML,
                message="Please send hashable yaml ..."
            ).get_bytes()

    # load hashable
    print(_hashable_yaml)
    return Response(
        status=Status.STARTED, message="Just started"
    ).get_bytes()


def invoke_for_hashable_on_client(request: "Request") -> t.Any:
    _start = _now()
    print("...................................11111111111111111111111111111")
    with DAPR.client as _client:
        print("...................................222222222222222222222", (_now() - _start).total_seconds())
        # noinspection PyTypeChecker
        _response = _client.invoke_method(
            app_id=DAPR.APP_ID,
            method_name="invoke_for_hashable_on_server",
            data=request.get_bytes(),
            content_type='text/plain',
            http_verb='GET',
            # http_querystring=(
            #     ('key1', 'value1')
            # ),
        )
        print("...................................33333333333333333", (_now() - _start).total_seconds())

        print(_response)


class Status(enum.Enum):
    NEEDS_HASHABLE_YAML = enum.auto()
    STARTED = enum.auto()
    PROCESSING = enum.auto()
    COMPLETED = enum.auto()


class Response(t.NamedTuple):
    """
    Note that we don't want to add more fields to this tuple and might not be needed as
      simple design is best ...

    todo: DaprClient.invoke_method data kwarg is used to send kwargs for hashable method
      Note that they are serialized with json.dumps instead of pickle.dumps as there
      is encoding problem ... as of now request data sent to server will be small so
      we might not need to worry

    todo: I assume pickles are easy and more powerful as of now ... KEEP THINGS SIMPLE
      Ignore below comments if you agree ...
      ** IGNORE BELOW **
      In long run we will might think of removing pickle and see if json can be sent
      back with data as protobuf which can be deserialized on client.
      Where class_name can create instance with data for display.
       {
          'status': <>,
          'message': <>,
          'class_name': <>,
          'module_name': <>,
          'data': <protobuf>,
       }
    """
    status: Status
    message: str
    # Any serializable python object
    # Note that according to pyarrow `pa.Table` are also serializable
    data: t.Any = None

    @property
    def is_completed(self):
        return self.status is Status.COMPLETED

    @property
    def is_processing(self):
        return self.status in [Status.PROCESSING, Status.STARTED]

    @property
    def just_started(self):
        return self.status is Status.STARTED

    @property
    def results_available(self):
        return self.data is not None

    def get_bytes(self) -> bytes:
        return zlib.compress(pickle.dumps(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        return pickle.loads(zlib.decompress(data))


class Request(t.NamedTuple):
    """
    Note that we don't want to add more fields to this tuple and might not be needed as
      simple design is best ...
    """
    yaml: str
    fn_name: str
    kwargs: t.Dict

    def get_bytes(self) -> bytes:
        return zlib.compress(pickle.dumps(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> "Request":
        return pickle.loads(zlib.decompress(data))


class Invoke:
    """

    Works for endpoint as given by
    >>> invoke_for_hashable_on_client
    >>> invoke_for_hashable_on_server

    This will be used as decorator for `m.HashableClass` methods which will be
    converted to dapr invoke commands on remote machines (needs configuration)

    Note that you need not know dapr just decorate configure ip address and run.

    todo: send toolcraft version also to check if same toolcraft version is
      installed on remote machine ...

    todo: some git-hash check to confirm if remote machine has same version ...
      note that hash should be for the user code who uses this library and not for
      toolcraft ...
    """

    def __init__(self):
        ...

    def __call__(self, fn: t.Callable):
        # wrap fn
        def _fn(_self: m.HashableClass, **kwargs):
            print(_self.yaml(), kwargs)
            if DAPR.MODE is DaprMode.client:
                return invoke_for_hashable_on_client(
                    request=Request(
                        yaml=_self.yaml(),
                        fn_name=fn.__name__,
                        kwargs=kwargs,
                    )
                )
            elif DAPR.MODE is DaprMode.server:
                return fn(_self, **kwargs)
            else:
                e.code.NotAllowed(
                    msgs=[
                        f"DaprMode {DAPR.MODE} is not supported by decorator "
                        f"{self.__class__}"
                    ]
                )

        return _fn
