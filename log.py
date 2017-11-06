#!/usr/bin/env python3

"""Handle logging"""

import logging
import os

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))


def _getlogger(
        logname='jupyter-mortgage',
        logfile=os.path.join(SCRIPTDIR, 'log.txt')):
    """Get a logger

    Exists basically just so we don't pullute global namespace with handler lol
    """
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(logfile)
    handler.setFormatter(logging.Formatter('%(levelname)s %(filename)s:%(lineno)s:%(funcName)s(): %(message)s'))
    log.addHandler(handler)
    return log


LOG = _getlogger()
