#!/usr/bin/env python3

"""Utilities for jupyter-mortgage"""

import logging


def getlogger():
    """Get a logger

    This function basically just exists so I don't pollute the global
    namespace with conhandler. Lol.
    """
    log = logging.getLogger('jupyter-mortgage')
    log.setLevel(logging.WARNING)
    conhandler = logging.StreamHandler()
    conhandler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.addHandler(conhandler)
    return log
