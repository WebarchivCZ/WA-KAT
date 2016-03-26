#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module handles list of Aleph's keywords, provides REST API with this
keywords and allows translation of those keywords to their codes and so on.
"""
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
    """
    Read content of the file containing keyword informations in JSON. File is
    packed using BZIP.

    Returns:
        list: List of dictionaries containing keywords.
    """
    self_path = os.path.dirname(__file__)
    kw_list_path = join(self_path, "../templates/keyword_list.json.bz2")

    with bz2.BZ2File(kw_list_path) as f:
        kw_list = f.read()

    return json.loads(kw_list)


def build_kw_dict(kw_list):
    """
    Build keyword dictionary from raw keyword data. Ignore invalid or
    invalidated records.

    Args:
        kw_list (list): List of dicts from :func:`read_kw_file`.

    Returns:
        OrderedDict: dictionary with keyword data.
    """
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
KW_DICT = None  #: Output from :func:`build_kw_dict`.
KEYWORDS = None  #: List of strings with keywords.
KEYWORDS_LOWER = None  #: List of strings with keywords.lower()

#: Path to the unpacked keyword list in /tmp. This is used as bottle
#: optimization.
KW_CACHE_PATH = None


def init():
    """
    Initialize all global variables (:attr:`.KW_DICT`, :attr:`.KEYWORDS`,
    :attr:`.KEYWORDS_LOWER`, :attr:`.KW_CACHE_PATH`) to their values.

    Global variables are then used from analyzers and so on.
    """
    global _INITIALIZED

    if _INITIALIZED:
        return

    global KW_DICT
    global KEYWORDS
    global KW_CACHE_PATH
    global KEYWORDS_LOWER

    KW_DICT = build_kw_dict(read_kw_file())
    KEYWORDS = sorted([k.decode("utf-8") for k in KW_DICT.keys()])
    KEYWORDS_LOWER = {
        k.lower(): k
        for k in KEYWORDS
    }
    keywords_json = json.dumps(KEYWORDS)
    KW_CACHE_PATH = "/tmp/wa_kat_cache_keywords.json"

    # create cached files
    with open(KW_CACHE_PATH, "w") as f:
        f.write(keywords_json)
    with open(KW_CACHE_PATH + ".gz", "w") as f:
        to_gzipped_file(keywords_json, out=f)

    _INITIALIZED = True


init()


# Functions ===================================================================
def keyword_to_info(keyword):
    """
    Get keyword dict based on the `keyword`.

    Args:
        keyword (str): Keyword as string.

    Returns:
        dict: Additional keyword info.
    """
    return KW_DICT.get(keyword)


# API =========================================================================
@get(join(API_PATH, "kw_list.json"))
def get_kw_list():
    """
    Virtual ``kw_list.json`` file.

    List of all keywords on one JSON page. This is later used by the typeahead
    script, which shows keyword hints to user.
    """
    response.content_type = RESPONSE_TYPE

    return gzip_cache(KW_CACHE_PATH)
