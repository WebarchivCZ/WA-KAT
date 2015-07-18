#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.title_detector import get_titles


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML>
<head>
    <title>HTML title</title>

    <meta name    = "DC.Title"
          lang    = "en"
          content = "Dublin Core title">

    <meta name    = "DC.Title"
          lang    = "cs"
          content = "Dublin Core titulek">

    <meta name    = "title"
          content = "<meta> title">
</head>
<body>
Somecontent.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_titles():
    titles = get_titles(TEST_TEMPLATE)

    assert titles[0] == "HTML title"
    assert titles[0].source == "HTML"

    assert titles[1] == "<meta> title"
    assert titles[1].source == "Meta"

    assert titles[2] == "Dublin Core title"
    assert titles[2].source == "DC"
    assert titles[3] == "Dublin Core titulek"
    assert titles[3].source == "DC"

