#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wa_kat.analyzers.source_string import SourceString


# Tests =======================================================================
def test_source_string():
    assert SourceString("azgabash") == "azgabash"
    assert SourceString("azgabash", source="DC") == "azgabash"

    assert "DC" in SourceString("azgabash", source="DC").__repr__()
