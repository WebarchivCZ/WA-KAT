#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.place_detector import get_place_tags


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML>
<head>
    <title>HTML title</title>

    <meta name    = "geo.placename"
          content = "Praha">
</head>
<body>
Somecontent.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_place_tags():
    place_tags = get_place_tags(TEST_TEMPLATE, "nkp.cz")

    assert place_tags[0] == "Praha"
    assert place_tags[0].source == "HTML"

    assert place_tags[1] == "Narodni knihovna Ceske republiky, Klementinum 190, Praha 1, 110 00, The Czech Republic"
    assert place_tags[1].source == "Whois"
