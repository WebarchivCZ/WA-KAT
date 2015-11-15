#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.keyword_detector import get_keyword_tags


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML>
<head>
    <title>HTML title</title>

    <meta name    = "keywords"
          content = "html, keywords">

    <meta name    = "DC.Keywords"
          content = "first second third">
</head>
<body>
Zde je nějaký obsah, ze kterého by se měly správně vyextrahovat klíčová slova,
jako třeba azgabash, nebo hardware. Naopak běžná slova by měla být ignorována.

Tyto slova je pak třeba porovnat ještě s nějakým setem podporovaných slov v
národní knihovně.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_keyword_tags():
    keywords = get_keyword_tags(TEST_TEMPLATE)

    assert keywords[0] == "html"
    assert keywords[0].source == "HTML"

    assert keywords[1] == "keywords"
    assert keywords[1].source == "HTML"

    assert keywords[2] == "first"
    assert keywords[2].source == "DC"

    assert keywords[3] == "second"
    assert keywords[3].source == "DC"

    assert keywords[4] == "third"
    assert keywords[4].source == "DC"

    # TODO: free text keyword extraction
    # assert keywords[5] == "azgabash"
    # assert keywords[5].source == "text"

    # assert keywords[6] == "hardware"
    # assert keywords[6].source == "text"
