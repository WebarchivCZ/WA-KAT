#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import OrderedDict

from xmltodict import unparse
from odictliteral import odict


# Variables ===================================================================
# Functions & classes =========================================================
def remove_none(data):
    if isinstance(data, list) or isinstance(data, tuple):
        return [x for x in data if x is not None]

    out = OrderedDict()
    for key, val in data.iteritems():
        if val is not None:
            out[key] = val

    return out


def compose_metadata(data):
    def compose(val, arguments=None):
        if val is None:
            return None

        if not arguments:
            return val

        arguments["#text"] = val
        return arguments

    conspect = data.get("conspect", {})

    author_name = data.get("author", {}).get("name")
    author_code = data.get("author", {}).get("code")

    metadata = odict[
        "dc:title": data.get("title"),
        "dcterms:alternative": data.get("subtitle"),
        "dc:creator": compose(author_name, {"@id": author_code}),
        "dc:publisher": data.get("publisher"),
        "dc:description": data.get("annotation"),
        "dc:coverage": compose(data.get("place"), {"@xml:lang": "cze"}),
        "dc:language": compose(data.get("language"), {"@schema": "ISO 639-2"}),
        "dcterms:created": data.get("from_year"),
        "dcterms:accrualperiodicity": compose(
            data.get("periodicity"),
            {"@xml:lang": "cze"}
        ),
        "dc:identifier": [
            {"@rdf:resource": data["url"]},
            compose(data.get("issn"), {"@xsi:type": "ISSN"}),
            compose(conspect.get("mdt"), {"@xsi:type": "MDT"}),
            compose(conspect.get("ddc"), {"@xsi:type": "DDC"}),
        ],
        "dc:subject": [
            compose(conspect.get("mdt"), {"@xsi:type": "dcterms:UDC"}),
            compose(conspect.get("ddc"), {"@xsi:type": "dcterms:DDC"}),
        ],
    ]

    def pick_keywords(data, source):
        return [
            x["zahlavi"]
            for x in data.get(source, [])
            if x.get("zahlavi")
        ]

    # parse and add keywords (keywords are in dicts with other data, I want
    # just the free-text descriptions)
    cz_keywords = pick_keywords(data, "cz_keywords")
    en_keywords = pick_keywords(data, "en_keywords")

    if cz_keywords:
        metadata["dc:subject"].append({
            "@xml:lang": "cz",
            "#text": ", ".join(cz_keywords)
        })
    if en_keywords:
        metadata["dc:subject"].append({
            "@xml:lang": "en",
            "#text": ", ".join(en_keywords)
        })

    # filter unset identifiers - TODO: rewrite to recursive alg.
    metadata["dc:identifier"] = [x for x in metadata["dc:identifier"] if x]
    metadata["dc:subject"] = [x for x in metadata["dc:subject"] if x]

    return metadata


def to_dc(data):
    root = odict[
        "metadata": odict[
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xmlns:dc": "http://purl.org/dc/elements/1.1/",
            "@xmlns:dcterms": "http://purl.org/dc/terms/",
            "@xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        ]
    ]

    # map metadata to the root element, skip None values
    for key, val in compose_metadata(remove_none(data)).iteritems():
        if val is None:
            continue

        if isinstance(val, basestring) and not val.strip():
            continue

        if isinstance(val, str):
            val = val.decode("utf-8")

        root["metadata"][key] = val

    return unparse(root, pretty=True)
