#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from shared import parse_meta


# Functions & classes =========================================================
def _get_html_authors(index_page):
    """
    Return list of `authors` from HTML ``<meta>`` tags.
    """
    return parse_meta(index_page, "author", "HTML")


def _get_dc_authors(index_page):
    """
    Return list of `authors` parsed from dublin core.
    """
    return parse_meta(index_page, "DC.Creator", "DC")


def get_author(index_page):
    """
    Parse `authors` from HTML ``<meta>`` and dublin core.
    """
    dom = dhtmlparser.parseString(index_page)

    authors = [
        _get_html_authors(dom),
        _get_dc_authors(dom),
    ]

    return sum(authors, [])  # return flattened list
