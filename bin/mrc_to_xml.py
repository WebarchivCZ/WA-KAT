#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import os.path
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from wa_kat.convertors.mrc_to_marc import mrc_to_marc


# Functions & classes =========================================================
def convert_file(fn):
    if not os.path.exists(fn):
        sys.stderr.write("Can't open `%s`!\n" % fn)
        sys.exit(1)

    with open(fn) as f:
        data = f.read()

    return mrc_to_marc(data)


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "INPUT",
        nargs=1,
        help="Input file."
    )

    args = parser.parse_args()

    print convert_file(args.INPUT[0])
