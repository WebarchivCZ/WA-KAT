#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import argparse
from os.path import join
from os.path import dirname

from bottle import run

sys.path.insert(0, join(dirname(__file__), "../src"))
from wa_kat import rest_api  # for Bottle applications
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
    # to add help with name and short description
    parser = argparse.ArgumentParser(
        description="WA-KAT server runner."
    )
    args = parser.parse_args()

    print "Waiting for ZEO connection.."
    main()
