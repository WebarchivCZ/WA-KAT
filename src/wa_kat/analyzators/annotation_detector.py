#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from .shared import parse_meta


# Functions & classes =========================================================
def _get_html_annotations(index_page):
    """
    Return `descriptions` stored in ``<meta>`` tags.
    """
    return parse_meta(index_page, "description", "Meta")


def _get_dc_annotations(index_page):
    """
    Return `description` stored in dublin core ``<meta>`` tags.
    """
    return parse_meta(index_page, "dc.description", "DC")


def get_annotations(index_page):
    """
    Return list of descriptions parsed from ``<meta>`` tags and dublin core
    inlined in ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of ``SourceString`` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    descriptions = [
        _get_html_annotations(dom),
        _get_dc_annotations(dom),
    ]

    return sum(descriptions, [])  # return flatterned list
