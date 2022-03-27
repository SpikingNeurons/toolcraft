"""
todo explore asyncio: courotines, futures, streams
  https://docs.python.org/3/library/asyncio-stream.html

todo: explore reverse proxy
  https://www.youtube.com/watch?v=5u1YDR4W7Ic
  It can also provide login with static sites like docausaurus
  Also it is possible to scale independent components rather than entire application
  It also is sutable for building systems behind firewall
  Something to do with SSO as well

"""
from .__base__ import DaprMode, HashableRunner
from .invoke import Invoke, Response
