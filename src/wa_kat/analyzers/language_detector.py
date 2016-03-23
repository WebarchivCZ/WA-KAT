#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Parse and guess information about language of the resource. Normalize the
language tags to ISO 639-2 format.
"""
#
# Imports =====================================================================
import langdetect
import dhtmlparser

from .shared import parse_meta
from .source_string import SourceString

from ..convertors.iso_codes import normalize


# Functions & classes =========================================================
def get_html_lang_tags(index_page):
    """
    Return `languages` stored in ``<meta>`` tags.

    ``<meta http-equiv="Content-language" content="cs">`` -> ``cs``

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    lang_tag = "content-language"
    lang_tags = dom.find(
        "meta",
        fn=lambda x: x.params.get("http-equiv", "").lower() == lang_tag
    )

    return [
        SourceString(tag.params["content"], "HTML")
        for tag in lang_tags
        if "content" in tag.params
    ]


def get_dc_lang_tags(index_page):
    """
    Return `languages` stored in dublin core ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "dc.language", "DC")


def detect_language(index_page):
    """
    Detect `languages` using `langdetect` library.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        obj: One :class:`.SourceString` object.
    """
    dom = dhtmlparser.parseString(index_page)

    clean_content = dhtmlparser.removeTags(dom)

    lang = None
    try:
        lang = langdetect.detect(clean_content)
    except UnicodeDecodeError:
        lang = langdetect.detect(clean_content.decode("utf-8"))

    return SourceString(
        lang,
        source="langdetect"
    )


def get_lang_tags(index_page):
    """
    Collect informations about language of the page from HTML and Dublin core
    tags and langdetect guesses.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    titles = [
        get_html_lang_tags(dom),
        get_dc_lang_tags(dom),
        [detect_language(dom)],
    ]

    return list({
        SourceString(normalize(lang), source=lang.source)
        for lang in sum(titles, [])
    })
