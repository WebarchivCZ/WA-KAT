#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from .shared import parse_meta


# Functions & classes =========================================================
def _get_html_annotations(web_index):
    """
    Return descriptions stored in ``<meta>`` tags.
    """
    return parse_meta(web_index, "description", "Meta")


def _get_dc_annotations(web_index):
    """
    Return description stored in dublin core ``<meta>`` tags.
    """
    return parse_meta(web_index, "DC.Description", "DC")


def get_annotations(web_index):
    """
    Return list of descriptions parsed from ``<meta>`` tags and dublin core
    inlined in ``<meta>`` tags.

    Args:
        web_index (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of ``SourceString`` objects.
    """
    dom = dhtmlparser.parseString(web_index)

    descriptions = [
        _get_html_annotations(dom),
        _get_dc_annotations(dom),
    ]

    return sum(descriptions, [])  # return flatterned list
