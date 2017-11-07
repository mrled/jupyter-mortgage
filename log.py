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

    logfmt = '%(levelname)s %(asctime)s %(filename)s:%(lineno)s:%(funcName)s(): %(message)s'
    datefmt = '%Y%m%d-%H%M%S'

    fhandler = logging.FileHandler(logfile)
    fhandler.setFormatter(logging.Formatter(logfmt, datefmt=datefmt))
    log.addHandler(fhandler)

    # shandler = logging.StreamHandler()
    # shandler.setFormatter(logging.Formatter(logfmt, datefmt=datefmt))
    # log.addHandler(shandler)

    return log


LOG = _getlogger()
