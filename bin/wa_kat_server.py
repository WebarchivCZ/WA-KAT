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

sys.path.insert(0, join(dirname(__file__), "../src"))  # TODO: relative/abs import

from wa_kat import rest_api
from wa_kat import bottle_index

from wa_kat import settings


# Functions & classes =========================================================
def main():
    run(
        server=settings.WEB_SERVER,
        host=settings.WEB_ADDR,
        port=settings.WEB_PORT,
        debug=settings.WEB_DEBUG,
        reloader=settings.WEB_RELOADER,
        quiet=settings.WEB_BE_QUIET,
    )


# Main program ================================================================
if __name__ == '__main__':
    main()
