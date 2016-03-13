#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from wa_kat.connectors import aleph


# Fixtures ====================================================================
@pytest.fixture
def issn():
    return "1805-8787"

# Tests =======================================================================
def test_by_issn(issn):
    assert aleph.by_issn(issn)


def test_authors_by_name():
    authors = list(aleph.Author.search_by_name("grada"))

    assert len(authors) >= 15

    assert "kn20080316009" in {aut.code for aut in authors}
