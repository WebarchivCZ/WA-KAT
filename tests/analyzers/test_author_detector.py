#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.author_detector import get_author_tags


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML>
<head>
    <title>HTML title</title>

    <meta name    = "dc.creator"
          content = "mr. Dublin Core">

    <meta name    = "author"
          content = "mr. Meta Author">
</head>
<body>
Somecontent.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_author_tags():
    authors = get_author_tags(TEST_TEMPLATE)

    assert authors[0] == "mr. Meta Author"
    assert authors[0].source == "HTML"

    assert authors[1] == "mr. Dublin Core"
    assert authors[1].source == "DC"
