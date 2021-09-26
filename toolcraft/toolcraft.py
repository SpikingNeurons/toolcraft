"""Main module."""

from . import (
    error,
    gui,
    helper,
    logger,
    marshalling,
    parallel,
    rules,
    settings,
    storage,
    util,
)

# todo: figure out where to do this check ... right now calling everytime
#  toolcraft is loaded ... can be done only when releasing package
rules.main()
