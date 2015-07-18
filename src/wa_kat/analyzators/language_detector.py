#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import langdetect
import dhtmlparser

from .shared import parse_meta
from .source_string import SourceString


# Functions & classes =========================================================
def _get_html_lang_tags(index_page):
    """
    Return `languages` stored in ``<meta>`` tags.

    ``<meta http-equiv="Content-language" content="cs">`` -> ``cs``
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


def _get_dc_lang_tags(index_page):
    """
    Return `languages` stored in dublin core ``<meta>`` tags.
    """
    return parse_meta(index_page, "dc.language", "DC")


def _detect_languages(index_page):
    """
    Detect `languages` using `langdetect` library.
    """
    dom = dhtmlparser.parseString(index_page)

    clean_content = dhtmlparser.removeTags(dom)

    return SourceString(
        langdetect.detect(clean_content),
        source="langdetect"
    )


def get_lang_tags(index_page):
    dom = dhtmlparser.parseString(index_page)

    titles = [
        _get_html_lang_tags(dom),
        _get_dc_lang_tags(dom),
        _detect_languages(dom),
    ]

    return sum(titles, [])  # return flatterned list
