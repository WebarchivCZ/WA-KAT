#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
from os.path import join
from os.path import dirname

from bottle import run

sys.path.insert(0, join(dirname(__file__), "../src"))

from wa_kat import settings
from wa_kat import bottle_index


# Functions & classes =========================================================
def main():
    bottle_index
    run(
        server=settings.WEB_SERVER,
        host=settings.WEB_ADDR,
        port=settings.WEB_PORT,
        debug=True,  #: TODO: don't forget to remove
        reloader=True  #: TODO: don't forget to remove
    )


# Main program ================================================================
if __name__ == '__main__':
    main()
