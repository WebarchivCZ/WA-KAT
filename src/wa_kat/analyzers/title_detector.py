#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from .shared import parse_meta
from source_string import SourceString


# Functions & classes =========================================================
def _get_html_titles(index_page):
    """
    Return list of titles parsed from HTML.
    """
    dom = dhtmlparser.parseString(index_page)

    title_tags = dom.find("title")

    return [
        SourceString(tag.getContent().strip(), "HTML")
        for tag in title_tags
        if tag.getContent().strip()
    ]


def _get_html_meta_titles(index_page):
    """
    Return list of titles parsed from ``<meta>`` tags.
    """
    return parse_meta(index_page, "title", "Meta")


def _get_dublin_core_titles(index_page):
    """
    Return list of titles parsed from dublin core inlined in ``<meta>``
    tags.
    """
    return parse_meta(index_page, "dc.title", "DC")


def get_title_tags(index_page):
    """
    Return list of titles parsed from HTML, ``<meta>`` tags and dublin core
    inlined in ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of ``SourceString`` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    titles = [
        _get_html_titles(dom),
        _get_html_meta_titles(dom),
        _get_dublin_core_titles(dom),
    ]

    return sum(titles, [])  # return flattened list
