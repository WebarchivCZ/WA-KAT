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
    assert aleph.by_issn(issn)


def test_authors_by_name():
    authors = list(aleph.Author.search_by_name("grada"))

    assert len(authors) >= 16

    assert "kn20080316009" in {aut.code for aut in authors}
