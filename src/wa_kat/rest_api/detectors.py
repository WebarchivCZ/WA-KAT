#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from os.path import join

from bottle import post
from bottle_rest import form_to_params


# Variables ===================================================================
API_PATH = "api_v1/detectors"


# Functions & classes =========================================================
@post(join(API_PATH, "title"))
@form_to_params
def detect_title(web_id):
    pass


@post(join(API_PATH, "author"))
@form_to_params
def detect_author(web_id):
    pass


@post(join(API_PATH, "keywords"))
@form_to_params
def detect_keywords(web_id):
    pass


@post(join(API_PATH, "creation_date"))
@form_to_params
def detect_creation_date(web_id):
    pass


@post(join(API_PATH, "language"))
@form_to_params
def detect_language(web_id):
    pass


@post(join(API_PATH, "place"))
@form_to_params
def detect_place(web_id):
    pass


@post(join(API_PATH, "annotation"))
@form_to_params
def detect_annotation(web_id):
    pass
