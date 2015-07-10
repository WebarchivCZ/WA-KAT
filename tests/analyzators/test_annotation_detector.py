#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzators.annotation_detector import get_annotations


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
def test_annotation_detector():
    descriptions = get_annotations(TEST_TEMPLATE)

    assert descriptions[0] == "Popis stránek."
    assert descriptions[0].source == "Meta"

    assert descriptions[1] == "Description of the web."
    assert descriptions[1].source == "DC"
