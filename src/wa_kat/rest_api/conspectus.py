#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
from os.path import join

from bottle import get
from bottle import response

from shared import API_PATH
from shared import RESPONSE_TYPE
from shared import read_template


# Functions & classes =========================================================
def conspect_to_dict(original):
    def _process_subcategories(sub_category):
        return {
            cat["name"]: cat["subcategory_id"]
            for cat in sub_category
        }

    conspect = {
        el["name"]: _process_subcategories(el["sub_categories"])
        for el in original
    }

    reverse = {
        el["name"]: el["id"]
        for el in original
    }

    return {
        "conspect": conspect,
        "conspect_to_id": reverse,
    }


def to_json(data):
    return json.dumps(
        data,
        indent=4,
        separators=(',', ': ')
    )


# Variables ===================================================================
CONSPECTUS = json.loads(read_template("conspectus.json"))
CONSPECTUS_DICT = conspect_to_dict(CONSPECTUS)
CONSPECTUS_JSON = to_json(CONSPECTUS_DICT)

EN_CONSPECTUS = json.loads(read_template("en_conspectus.json"))
EN_CONSPECTUS_DICT = conspect_to_dict(EN_CONSPECTUS)
EN_CONSPECTUS_JSON = to_json(EN_CONSPECTUS_DICT)


# API =========================================================================
@get(join(API_PATH, "conspect"))
def get_conspectus():
    response.content_type = RESPONSE_TYPE

    return CONSPECTUS_JSON
