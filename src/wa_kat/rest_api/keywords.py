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

from bottle import get

from shared import API_PATH
from shared import gzip_cache
from shared import to_gzipped_file


# Loaders =====================================================================
def read_kw_file():
    kw_list_path = join(
        os.path.dirname(__file__),
        "../templates/keyword_list.json.bz2"
    )

    with bz2.BZ2File(kw_list_path) as f:
        kw_list = f.read()

    return kw_list


# Variables ===================================================================
KW_DICT = read_kw_file()
KEYWORDS = [
    keyword_dict["zahlavi"]
    for keyword_dict in json.loads(KW_DICT)
]
KW_CACHE_PATH = "/tmp/wa_kat_cache_keywords.json"

# create cached files
with open(KW_CACHE_PATH, "w") as f:
    f.write(KW_DICT)
with open(KW_CACHE_PATH + ".gz", "w") as f:
    to_gzipped_file(KW_DICT, out=f)


# Functions ===================================================================
# API =========================================================================
@get(join(API_PATH, "kw_list.json"))
def get_kw_list():
    return gzip_cache(KW_CACHE_PATH)
