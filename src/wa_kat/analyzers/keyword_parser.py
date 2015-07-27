#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from shared import parse_meta
from source_string import SourceString


# Functions & classes =========================================================
def _get_html_keywords(index_page):
    """
    Return list of `keywords` parsed from HTML ``<meta>`` tags.
    """
    keywords = parse_meta(index_page, "keywords", "HTML")

    return [
        SourceString(keyword.strip(), "HTML")
        for keyword in keywords.split(",")
    ]


def _get_dc_keywords(index_page):
    """
    Return list of `keywords` parsed from dublin core.
    """
    keywords = parse_meta(index_page, "dc.keywords", "DC")

    return [
        SourceString(keyword, "DC")
        for keyword in keywords.split()
    ]


# def _extract_keywords_from_text(index_page):  # TODO: implement keyword parsing
#     pass


def get_keywords(index_page):
    """
    Parse `keywords` from HTML ``<meta>``, dublin core and from text.
    """
    dom = dhtmlparser.parseString(index_page)

    keywords = [
        _get_html_keywords(dom),
        _get_dc_keywords(dom),
        # [_extract_keywords_from_text(ip_address)],  # TODO: implement
    ]

    return sum(keywords, [])  # return flattened list
