#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.language_detector import get_lang_tags


# Variables ===================================================================
TEST_TEMPLATE = """
<HTML lang="ch" xml:lang="pl">
<head>
    <title>HTML title</title>

    <meta name    = "DC.Language"
          content = "en">

    <meta http-equiv="Content-language"
          content="fr">
</head>
<body>
Zde je nějaký ten obsah, který by měl být rozpoznaný jako čeština. Tím myslím vážně jako čeština, což zřejmě vyžaduje poněkud víc dat, než se mi původně chtělo psát.
</body>
</HTML>
"""


# Tests =======================================================================
def test_get_lang_tags():
    lang_tags_mapping = {
        x.source: x.__str__()
        for x in get_lang_tags(TEST_TEMPLATE)
    }

    assert lang_tags_mapping["langdetect"] == "cze"

    assert lang_tags_mapping["DC"] == "eng"

    assert lang_tags_mapping["HTML"] == "fre"

    assert lang_tags_mapping["<html lang=..>"] == "cha"

    assert lang_tags_mapping["<html xml:lang=..>"] == "pol"
