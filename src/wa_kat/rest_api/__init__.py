#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from os.path import join

from bottle import get
from bottle import post
from bottle_rest import form_to_params


# Variables ===================================================================
API_PATH = "api_v1/"


# Functions & classes =========================================================
@post(join(API_PATH, "register"))
@form_to_params
def register(url):
    pass


@get(join(API_PATH, "result"))
@form_to_params
def get_result(url):
    pass
