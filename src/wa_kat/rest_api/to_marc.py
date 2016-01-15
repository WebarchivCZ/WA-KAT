#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import os.path
from os.path import join

from marcxml_parser import MARCXMLRecord

from bottle import post
from bottle_rest import form_to_params

from shared import API_PATH


# Variables ===================================================================
# Functions & classes =========================================================
@post(join(API_PATH, "to_marc"))
@form_to_params
def to_marc(data):
    data = json.loads(data)

    return "ok"
