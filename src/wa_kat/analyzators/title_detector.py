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
def _detect_html_titles(web_index):
    """
    Return list of titles parsed from HTML.
    """
    dom = dhtmlparser.parseString(web_index)

    title_tags = dom.find("title")

    return [
        SourceString(tag.getContent().strip(), "HTML")
        for tag in title_tags
        if tag.getContent().strip()
    ]


def _detect_html_meta_titles(web_index):
    """
    Return list of titles parsed from ``<meta>`` tags.
    """
    return parse_meta(web_index, "title", "Meta")


def _detect_dublin_core_titles(web_index):
    """
    Return list of titles parsed from dublin core inlined in ``<meta>``
    tags.
    """
    return parse_meta(web_index, "dc.title", "DC")


def get_titles(web_index):
    """
    Return list of titles parsed from HTML, ``<meta>`` tags and dublin core
    inlined in ``<meta>`` tags.

    Args:
        web_index (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of ``SourceString`` objects.
    """
    dom = dhtmlparser.parseString(web_index)

    titles = [
        _detect_html_titles(dom),
        _detect_html_meta_titles(dom),
        _detect_dublin_core_titles(dom),
    ]

    return sum(titles, [])  # return flatterned list
