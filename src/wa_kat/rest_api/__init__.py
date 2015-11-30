#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import traceback
from os.path import join

from bottle import get
from bottle import post
from bottle import response
from bottle_rest import form_to_params

from ..zeo import RequestDatabase
from ..zeo import ConspectDatabase


# Variables ===================================================================
API_PATH = "/api_v1/"
RESPONSE_TYPE = "application/json; charset=utf-8"


# Functions & classes =========================================================
@post(join(API_PATH, "analyze"))
@form_to_params
def get_result(url):
    rd = RequestDatabase()
    response.content_type = RESPONSE_TYPE

    # handle cacheing
    try:
        ri = rd.get_request(url)

        if ri.is_old():
            print "Running the analysis"
            ri.paralel_processing()
    except Exception as e:
        return {
            "status": False,
            "error": e.message + "\n" + traceback.format_exc().strip()
        }

    print ri.to_dict()

    return {
        "status": True,
        "body": ri.to_dict()
    }


@get(join(API_PATH, "conspect"))
def get_conspect():
    cd = ConspectDatabase()
    response.content_type = RESPONSE_TYPE

    return json.dumps(cd.data)
