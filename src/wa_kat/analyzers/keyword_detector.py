#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from fuzzywuzzy import process

from shared import parse_meta
from source_string import SourceString

from ..rest_api.keywords import KEYWORDS


# Functions & classes =========================================================
def _get_html_keywords(index_page):
    """
    Return list of `keywords` parsed from HTML ``<meta>`` tags.
    """
    keyword_lists = (
        keyword_list.split(",")
        for keyword_list in parse_meta(index_page, "keywords", "HTML")
    )

    # create SourceStrings from the list of keywords
    return [
        SourceString(keyword.strip(), source="HTML")
        for keyword in sum(keyword_lists, [])  # flattern the list
    ]


def _get_dc_keywords(index_page):
    """
    Return list of `keywords` parsed from dublin core.
    """
    keyword_lists = (
        keyword_list.split()
        for keyword_list in parse_meta(index_page, "dc.keywords", "DC")
    )

    return [
        SourceString(keyword, source="DC")
        for keyword in sum(keyword_lists, [])  # flattern the list
    ]


# def _extract_keywords_from_text(index_page):  # TODO: implement keyword parsing
#     pass


def get_keyword_tags(index_page):
    """
    Parse `keywords` from HTML ``<meta>``, dublin core and from text.
    """
    dom = dhtmlparser.parseString(index_page)

    keywords = [
        _get_html_keywords(dom),
        _get_dc_keywords(dom),
        # _extract_keywords_from_text(index_page),  # TODO: implement
    ]

    return [
        SourceString(
            process.extractOne(str(keyword), KEYWORDS)[0].encode("utf-8"),
            source=keyword.source,
        )
        for keyword in sum(keywords, [])  # flattern
    ]
