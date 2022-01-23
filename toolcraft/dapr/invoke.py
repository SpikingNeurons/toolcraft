"""
Check dapr-grpc examples here
https://github.com/dapr/python-sdk/tree/master/examples

Some things to do based on this

1] invoke from client to hashable methods
  + See tutorial: rough_work/dapr/invoke
    Service invocation	Invoke service by passing bytes data
    Service invocation (advanced)	Invoke service by using custom protobuf message

"""

from .. import marshalling as m


class Invoke:
    """
    This will be used as decorator for `m.HashableClass` methods which will be
    converted to dapr invoke commands on remote machines (needs configuration)

    Note that you need not know dapr just decorate configure ip address and run.

    todo: send toolcraft version also to check if same toolcraft version is
      installed on remote machine ...

    todo: some git-hash check to confirm if remote machine has same version ...
      note that hash should be for the user code who uses this library and not for
      toolcraft ...
    """
    ...
