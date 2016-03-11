#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import bz2
import json
import os.path
from os.path import join
from collections import OrderedDict

from bottle import get
from bottle import response

from ..settings import API_PATH

from shared import gzip_cache
from shared import RESPONSE_TYPE
from shared import to_gzipped_file


# Loaders =====================================================================
def read_kw_file():
    kw_list_path = join(
        os.path.dirname(__file__),
        "../templates/keyword_list.json.bz2"
    )

    with bz2.BZ2File(kw_list_path) as f:
        kw_list = f.read()

    return json.loads(kw_list)


def build_kw_dict(kw_list):
    kw_dict = OrderedDict()
    sorted_list = sorted(
        kw_list,
        key=lambda x: x.get("zahlavi").encode("utf-8")
    )

    for keyword_data in sorted_list:
        if "zahlavi" not in keyword_data:
            continue

        zahlavi = keyword_data["zahlavi"].encode("utf-8")
        old_record = kw_dict.get(zahlavi)

        if not old_record:
            kw_dict[zahlavi] = keyword_data
            continue

        key = "angl_ekvivalent"
        if not old_record.get(key) and keyword_data.get(key):
            kw_dict[zahlavi] = keyword_data
            continue

        key = "zdroj_angl_ekvivalentu"
        if not old_record.get(key) and keyword_data.get(key):
            kw_dict[zahlavi] = keyword_data
            continue

        if len(str(keyword_data)) > len(str(old_record)):
            kw_dict[zahlavi] = keyword_data
            continue

    return kw_dict


# Variables ===================================================================
_INITIALIZED = False
KW_DICT = None
KEYWORDS = None
KW_CACHE_PATH = None


def init():
    global _INITIALIZED

    if _INITIALIZED:
        return

    global KW_DICT
    global KEYWORDS
    global KW_CACHE_PATH

    KW_DICT = build_kw_dict(read_kw_file())
    KEYWORDS = [k.decode("utf-8") for k in KW_DICT.keys()]
    KEYWORDS_JSON = json.dumps(KEYWORDS)
    KW_CACHE_PATH = "/tmp/wa_kat_cache_keywords.json"

    # create cached files
    with open(KW_CACHE_PATH, "w") as f:
        f.write(KEYWORDS_JSON)
    with open(KW_CACHE_PATH + ".gz", "w") as f:
        to_gzipped_file(KEYWORDS_JSON, out=f)

    _INITIALIZED = True


init()


# Functions ===================================================================
def keyword_to_info(keyword):
    return KW_DICT.get(keyword)


# API =========================================================================
@get(join(API_PATH, "kw_list.json"))
def get_kw_list():
    response.content_type = RESPONSE_TYPE

    return gzip_cache(KW_CACHE_PATH)
