#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from xmltodict import unparse
from odictliteral import odict


# Variables ===================================================================
# Functions & classes =========================================================
def compose_metadata(data):
    def compose(val, arguments=None):
        if val is None:
            return None

        if not arguments:
            return val

        arguments["#text"] = val
        return arguments

    conspect = data.get("conspect", {})

    metadata = odict[
        "dc:title": data.get("title"),
        "dcterms:alternative": data.get("subtitle"),
        "dc:publisher": data.get("publisher"),
        "dc:description": data.get("annotation"),
        "dc:language": compose(data.get("language"), {"@schema": "ISO 639-2"}),
        "dcterms:created": data.get("from_year"),
        "dc:identifier": [
            compose(data.get("issn"), {"@xsi:type": "ISSN"}),
            compose(conspect.get("mdt"), {"@xsi:type": "MDT"}),
            compose(conspect.get("ddc"), {"@xsi:type": "DDC"}),
        ],
        "dc:subject": [
            compose(conspect.get("mdt"), {"@xsi:type": "dcterms:UDC"}),
            compose(conspect.get("ddc"), {"@xsi:type": "dcterms:DDC"}),
        ],
    ]

    # filter unset identifiers - TODO: rewrite to recursive alg.
    metadata["dc:identifier"] = [x for x in metadata["dc:identifier"] if x]

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
    for key, val in compose_metadata(data).iteritems():
        if val is None:
            continue

        if isinstance(val, basestring) and not val.strip():
            continue

        if isinstance(val, str):
            val = val.decode("utf-8")

        root["metadata"][key] = val

    return unparse(root, pretty=True)


print to_dc({
    "publisher": u"Sociologick\xfd \xfastav AV \u010cR v.v.i.,",
    "issn": "2336-2391",
    "subtitle": "",
    "periodicity": u"\u010cast\xe9 aktualizace",
    "language": "cze",
    "author": None,
    "url": "http: //dav.soc.cas.cz",
    "cz_keywords": [
        {
            "zahlavi": "keyboard",
            "uid": "ph117670",
            "zdroj": "czenas"
        }, {
            "zahlavi": u"ANCA asociovan\xe1 vaskulitida",
            "uid": "ph568406",
            "zdroj": "czenas"
        }
    ],
    "conspect": {
        "ddc": "580",
        "en_name": "Plants",
        "conspect_id": "2",
        "mdt": "58",
        "name": "Botanika"
    },
    "annotation": u"N\u011bjak\xfd popisek.",
    "rules": {
        "youtube": False,
        "javascript": False,
        "calendars": False,
        "budget": 15000,
        "frequency": 365,
        "global_reject": True,
        "gentle_fetch": "default",
        "local_traps": False
    },
    "to_year": "9999",
    "place": "Praha",
    "from_year": "2007",
    "title": u"Data a v\xfdzkum - SDA Info",
    "creation_date": "2007-",
    "en_keywords": [
        {
            "zahlavi": "keyboard (musical instrument)",
            "zdroj": "eczenas"
        }, {
            "zahlavi": "ANCA-associated vasculitis",
            "zdroj": "eczenas"
        }
    ],
    "additional_info": {
        "776": u"7760  L $$tData a v\xfdzkum (Print)$$x1802-8152",
        "008": "008   L 131210c20079999xr-f||p|s||||||---b0mul-c",
        "222": u"222 0 L $$aData a v\xfdzkum - SDA Info$$b(On-line)",
        "PER": "PER   L $$a2x za rok"
    },
    "mdt": [
        {
            "mrf": "MRF",
            "mdt": "681.828: 681.816"
        }, {
            "mrf": "MRF",
            "mdt": "616.13/.14-002:616.155.3-097"
        }
    ]
})
