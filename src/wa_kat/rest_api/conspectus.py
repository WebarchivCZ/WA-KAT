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

from shared import to_json
from shared import API_PATH
from shared import RESPONSE_TYPE
from shared import read_template


# Conspect convertor ==========================================================
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


def sub_to_consp_dict(consp_dict):
    """
    Create reverse mapping, which returns following dict::

        "sub_code": {
            "sub_code": subconspect code,
            "sub_name": subconspect name,
            "consp_id": conspect id,
            "consp_name": conspect name,
        }
    """
    reverse_mapping = {}
    for conspectus in consp_dict:
        for sub_consp in conspectus.get("sub_categories", []):
            reverse_mapping[sub_consp["subcategory_id"]] = {
                "sub_code": sub_consp["subcategory_id"],
                "sub_name": sub_consp["name"],
                "consp_id": conspectus["id"],
                "consp_name": conspectus["name"],
            }

    return reverse_mapping


# Variables ===================================================================
CONSPECTUS = json.loads(read_template("conspectus.json"))
CONSPECTUS_DICT = conspect_to_dict(CONSPECTUS)
CONSPECTUS_JSON = to_json(CONSPECTUS_DICT)

EN_CONSPECTUS = json.loads(read_template("en_conspectus.json"))
EN_CONSPECTUS_DICT = conspect_to_dict(EN_CONSPECTUS)
EN_CONSP_REV_DICT = sub_to_consp_dict(EN_CONSPECTUS)
EN_CONSPECTUS_JSON = to_json(EN_CONSPECTUS_DICT)


# Functions ===================================================================
def find_en_conspectus(sub_code):
    return EN_CONSP_REV_DICT.get(sub_code)


# API =========================================================================
@get(join(API_PATH, "conspect.json"))
def get_conspectus():
    response.content_type = RESPONSE_TYPE

    return CONSPECTUS_JSON


@get(join(API_PATH, "en_conspect.json"))
def get_en_conspectus():
    response.content_type = RESPONSE_TYPE

    return EN_CONSPECTUS_JSON
