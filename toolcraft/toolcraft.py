"""Main module."""

from . import logger, settings, marshalling, util, error, helper, parallel, \
    rules, gui, storage


# todo: figure out where to do this check ... right now calling everytime
#  toolcraft is loaded ... can be done only when releasing package
rules.main()
