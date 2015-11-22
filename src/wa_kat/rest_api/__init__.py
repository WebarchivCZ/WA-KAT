#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from os.path import join

from bottle import get
from bottle import post
from bottle_rest import form_to_params

from ..zeo import RequestDatabase


# Variables ===================================================================
API_PATH = "api_v1/"


# Functions & classes =========================================================



@post(join(API_PATH, "register"))
@form_to_params
def get_result(url):
    rd = RequestDatabase()

    # handle cacheing
    try:
        ri = rd.get_request(url)

        if ri.is_old():
            ri.paralel_processing()
    except Exception as e:
        return {
            "status": False,
            "error": e.message
        }

    return {
        "status": True,
        "body": ri.to_dict()
    }
