#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest


# Variables ===================================================================
print to_dc({
    "publisher": u"Sociologick\xfd \xfastav AV \u010cR v.v.i.,",
    "issn": "2336-2391",
    "subtitle": "",
    "periodicity": u"\u010cast\xe9 aktualizace",
    "language": "cze",
    "author": None,
    "url": "http://dav.soc.cas.cz",
   "author": {
    "linked_forms": [
        "Grada Publishing a.s.",
        "Grada (nakladatelstv\xed)",
        "Nakladatelstv\xed Grada"
    ],
    "name": "Grada Publishing",
    "is_corporation": True,
    "record": {
        "i1": "2",
        "i2": " ",
        "a": ["Grada Publishing"],
        "b": " ",
        "7": ["kn20080316009"]
    },
    "code": "kn20080316009",
    "alt_name": "Grada Publishing [organizace] (Grada Publishing a.s., Grada (nakladatelstv\xed), Nakladatelstv\xed Grada)"
   },
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


# Fixtures ====================================================================
# @pytest.fixture
# def fixture():
#     pass

# with pytest.raises(Exception):
#     raise Exception()


# Tests =======================================================================
def test_():
    pass
