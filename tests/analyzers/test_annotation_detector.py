#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.annotation_detector import get_annotation_tags


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML>
<head>
    <meta name="description"
          content="Popis stránek.">.

    <meta name    = "DC.Description"
          content = "Description of the web.">
</head>
<body>
Somecontent.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_annotation_tags():
    descriptions = get_annotation_tags(TEST_TEMPLATE)

    assert descriptions[0] == "Popis stránek."
    assert descriptions[0].source == "Meta"

    assert descriptions[1] == "Description of the web."
    assert descriptions[1].source == "DC"
