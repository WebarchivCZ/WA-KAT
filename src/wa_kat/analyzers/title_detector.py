#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used to detect titles of the webpages from several sources.
"""
#
# Imports =====================================================================
import dhtmlparser

from .shared import parse_meta
from source_string import SourceString


# Functions & classes =========================================================
def get_html_titles(index_page):
    """
    Return list of titles parsed from HTML.

    Args:
        index_page (str): HTML content of the page you wish to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    title_tags = dom.find("title")

    return [
        SourceString(tag.getContent().strip(), "HTML")
        for tag in title_tags
        if tag.getContent().strip()
    ]


def get_html_meta_titles(index_page):
    """
    Return list of titles parsed from ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wish to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "title", "Meta")


def get_dublin_core_titles(index_page):
    """
    Return list of titles parsed from dublin core inlined in ``<meta>``
    tags.

    Args:
        index_page (str): HTML content of the page you wish to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "dc.title", "DC")


def get_title_tags(index_page):
    """
    Collect data from all the functions defined in this module and return list
    of titles parsed from HTML, ``<meta>`` tags and dublin core inlined in
    ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wish to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    titles = [
        get_html_titles(dom),
        get_html_meta_titles(dom),
        get_dublin_core_titles(dom),
    ]

    return sum(titles, [])  # return flattened list
