#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Parse informations about authors from HTML ``<meta>`` tags and
`Dublin core <http://dublincore.org>`_.
"""
#
# Imports =====================================================================
import dhtmlparser

from shared import parse_meta


# Functions & classes =========================================================
def get_html_authors(index_page):
    """
    Return list of `authors` from HTML ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "author", "HTML")


def get_dc_authors(index_page):
    """
    Return list of `authors` parsed from dublin core.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "DC.Creator", "DC")


def get_author_tags(index_page):
    """
    Parse `authors` from HTML ``<meta>`` and dublin core.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    authors = [
        get_html_authors(dom),
        get_dc_authors(dom),
    ]

    return sum(authors, [])  # return flattened list
