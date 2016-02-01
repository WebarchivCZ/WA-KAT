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

from ..zeo import ConspectDatabase

from shared import API_PATH
from shared import RESPONSE_TYPE


# Variables ===================================================================
# Functions & classes =========================================================
@get(join(API_PATH, "conspect"))
def get_conspectus():
    cd = ConspectDatabase()
    response.content_type = RESPONSE_TYPE

    return json.dumps(cd.data)
