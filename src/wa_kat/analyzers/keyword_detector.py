#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Parse keywords from HTML meta tags and `Dublin core <http://dublincore.org>`_.
Try to analyze the text on the page and return list of tags found there.

Module maps the parserd keywords to currated keywords used in
`Aleph <http://ntk.cz>`_.
"""
#
# Imports =====================================================================
import dhtmlparser
from HTMLParser import HTMLParser

from textblob import TextBlob
from fuzzywuzzy import process

from shared import parse_meta
from source_string import SourceString

from ..rest_api.keywords import KEYWORDS
from ..rest_api.keywords import KEYWORDS_LOWER


# Functions & classes =========================================================
class MLStripper(HTMLParser):
    """
    Class used to strip HTML from tags.
    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    @classmethod
    def strip_tags(cls, html):
        """
        This function may be used to remove HTML tags from data.
        """
        s = cls()
        s.feed(html)

        return s.get_data()


def get_html_keywords(index_page):
    """
    Return list of `keywords` parsed from HTML ``<meta>`` tags.

    Args:
        index_page (str): Content of the page as UTF-8 string

    Returns:
        list: List of :class:`.SourceString` objects.
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


def get_dc_keywords(index_page):
    """
    Return list of `keywords` parsed from Dublin core.

    Args:
        index_page (str): Content of the page as UTF-8 string

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    keyword_lists = (
        keyword_list.split()
        for keyword_list in parse_meta(index_page, "dc.keywords", "DC")
    )

    return [
        SourceString(keyword, source="DC")
        for keyword in sum(keyword_lists, [])  # flattern the list
    ]


def extract_keywords_from_text(index_page, no_items=5):
    """
    Try to process text on the `index_page` deduce the keywords and then try
    to match them on the Aleph's dataset.

    Function returns maximally `no_items` items, to prevent spamming the user.

    Args:
        index_page (str): Content of the page as UTF-8 string
        no_items (int, default 5): Number of items to return.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    index_page = MLStripper.strip_tags(index_page)
    tokenized_index = TextBlob(index_page).lower()

    present_keywords = [
        KEYWORDS_LOWER[key]
        for key in KEYWORDS_LOWER.keys()
        if len(key) > 3 and key in tokenized_index
    ]

    def to_source_string(key):
        source = "Keyword analysis"
        try:
            return SourceString(key, source)
        except UnicodeEncodeError:
            return SourceString(key.encode("utf-8"), source)

    multi_keywords = [
        to_source_string(key)
        for key in present_keywords
        if tokenized_index.words.count(key) >= 1
    ]

    multi_keywords = sorted(multi_keywords, key=lambda x: len(x), reverse=True)

    if len(multi_keywords) > no_items:
        return multi_keywords[:no_items]

    return multi_keywords


def get_keyword_tags(index_page, map_to_nk_set=True):
    """
    Parse `keywords` from HTML ``<meta>``, dublin core and from text.

    Args:
        index_page (str): Content of the page as UTF-8 string.
        map_to_nk_set (bool): Should the algorithm try to map keywords to
            keywords used in NK?

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    dom = dhtmlparser.parseString(index_page)

    keywords = [
        get_html_keywords(dom),
        get_dc_keywords(dom),
    ]
    # do not try to match extracted_keywords, because they are based on Aleph's
    # dataset
    extracted_keywords = extract_keywords_from_text(index_page)

    keywords = sum(keywords, [])  # flattern

    if not map_to_nk_set:
        return keywords + extracted_keywords

    def try_match(keyword):
        """
        This provides chance to speed up the process a little.
        """
        kw = KEYWORDS_LOWER.get(keyword.lower())
        if kw:
            return kw

        return process.extractOne(str(keyword), KEYWORDS)[0].encode("utf-8")

    keywords = [
        SourceString(
            try_match(keyword),
            source=keyword.source,
        )
        for keyword in keywords
    ]

    return sorted(list(set(keywords + extracted_keywords)))
