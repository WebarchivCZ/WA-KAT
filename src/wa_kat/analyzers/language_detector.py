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

from ..convertors.iso_codes import normalize


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


def _detect_language(index_page):
    """
    Detect `languages` using `langdetect` library.
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
    dom = dhtmlparser.parseString(index_page)

    titles = [
        _get_html_lang_tags(dom),
        _get_dc_lang_tags(dom),
        [_detect_language(dom)],
    ]

    return list({
        SourceString(normalize(lang), source=lang.source)
        for lang in sum(titles, [])
    })
