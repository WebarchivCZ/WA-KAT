#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from source_string import SourceString


# Functions & classes =========================================================
def parse_meta(content, meta_name, source_descr, content_attr_name="content"):
    """
    Return list of strings parsed from `content` attribute from ``<meta>``
    tags with given `meta_name`.
    """
    dom = dhtmlparser.parseString(content)

    title_tags = dom.find(
        "meta",
        fn=lambda x: x.params.get("name", "").lower() == meta_name.lower()
    )

    return [
        SourceString(tag.params[content_attr_name], source_descr)
        for tag in title_tags
        if content_attr_name in tag.params
    ]
