#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from wa_kat.connectors import aleph


# Variables ===================================================================



# Fixtures ====================================================================
@pytest.fixture
def issn():
    return "1805-8787"

# with pytest.raises(Exception):
#     raise Exception()


# Tests =======================================================================
def test_by_issn(issn):
    aleph.by_issn(issn)
