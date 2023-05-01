"""
Aim is to implement ASGI server

todo: support either Uvicorn of Hypercorn
  + best thing is hypercorn supports http2 i.e. grpc kind of thing
  + we want to stream/return results from server that run `toolcraft.job.Job`
    to client so we need some sort of ASGi server running on server that can
    take in multiple requests and run them in async on server
  + needed by texipy so that make pdf can be called as and when any file changes
    Have a design which can augment toolcraft.job or have separate module called
    toolcraft.server
"""
