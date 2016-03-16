#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from xmltodict import unparse
from odictliteral import odict


# Variables ===================================================================
# Functions & classes =========================================================
def to_dc(data):
    root = odict[
        "metadata": odict[
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xmlns:dc": "http://purl.org/dc/elements/1.1/",
        ]
    ]

    metadata = odict[
        "dc:title": "title"
    ]

    for key, val in metadata.iteritems():
        root["metadata"][key] = val

    return unparse(root, pretty=True)


print to_dc(1)
