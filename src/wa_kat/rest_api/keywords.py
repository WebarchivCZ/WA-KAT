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
from bottle import response

from shared import gzipped
from shared import API_PATH
from shared import RESPONSE_TYPE


# Functions & classes =========================================================
def read_kw_file():
    kw_list_path = join(
        os.path.dirname(__file__),
        "../templates/keyword_list.json.bz2"
    )

    with bz2.BZ2File(kw_list_path) as f:
        kw_list = f.read()

    return json.loads(kw_list)


# Variables ===================================================================
KW_DICT = read_kw_file()
KEYWORDS = [
    keyword_dict["zahlavi"]
    for keyword_dict in KW_DICT
]


# API =========================================================================
@get(join(API_PATH, "kw_list.json"))
@gzipped
def get_kw_list():
    response.content_type = RESPONSE_TYPE

    return json.dumps(KEYWORDS)
