#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.convertors.mrc import val_to_mrc
from wa_kat.convertors.mrc import dicts_to_mrc

from marcxml_parser import MARCXMLRecord

import pytest


# Variables ===================================================================
RECORD_EXAMPLE = """
<?xml version = "1.0" encoding = "UTF-8"?>
<record>
<metadata>
<oai_marc>
<fixfield id="LDR">-----nai-a22------a-4500</fixfield>
<fixfield id="FMT">SE</fixfield>
<fixfield id="001">web20092023182</fixfield>
<fixfield id="003">CZ-PrNK</fixfield>
<fixfield id="005">20111130083047.0</fixfield>
<fixfield id="006">m--------d--------</fixfield>
<fixfield id="007">cr-cn-</fixfield>
<fixfield id="008">091130c20099999xr--x-w-s-----0---b2cze--</fixfield>
<varfield id="015" i1=" " i2=" ">
<subfield label="a">cnb002023182</subfield>
</varfield>
<varfield id="022" i1=" " i2=" ">
<subfield label="a">1804-1051</subfield>
</varfield>
<varfield id="040" i1="1" i2="2">
<subfield label="a">ABA001</subfield>
<subfield label="b">cze</subfield>
</varfield>
</oari_marc>
</metadata>
</record>
"""


# Fixtures ====================================================================
@pytest.fixture(scope="module")
def marc_record():
    return MARCXMLRecord(RECORD_EXAMPLE)


# Functions & classes =========================================================
def test_record(marc_record):
    assert marc_record["FMT"] == "SE"


def test_val_to_mrc(marc_record):
    assert val_to_mrc("FMT", marc_record["FMT"]) == "FMT   L SE"
    assert val_to_mrc("F", marc_record["FMT"]) == "F     L SE"


def test_dicts(marc_record):
    assert dicts_to_mrc("040", marc_record["040"]) == ["04012 L $$aABA001$$bcze"]
