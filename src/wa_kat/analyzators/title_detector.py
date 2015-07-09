#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

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
    dom = dhtmlparser.parseString(web_index)

    title_tags = dom.find(
        "meta",
        fn=lambda x: x.params.get("name", "").lower() == "title"
    )

    return [
        SourceString(tag.params["content"], "Meta")
        for tag in title_tags
        if "content" in tag.params
    ]


def _detect_dublin_core_titles(web_index):
    """
    Return list of titles parsed from dublin core inlined in ``<meta>``
    tags.
    """
    dom = dhtmlparser.parseString(web_index)

    title_tags = dom.find(
        "meta",
        fn=lambda x: x.params.get("name", "").lower() == "dc.title"
    )

    return [
        SourceString(tag.params["content"], "DC")
        for tag in title_tags
        if "content" in tag.params
    ]


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
