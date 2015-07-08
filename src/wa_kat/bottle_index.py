#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path

import requests
from bottle import get
from bottle import abort
from bottle import request
from bottle import static_file

from . import settings


# Variables ===================================================================
TEMPLATE_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "templates"
)
INDEX_PATH = os.path.join(TEMPLATE_PATH, "index_vertical.html")
STATIC_PATH = os.path.join(TEMPLATE_PATH, "static")


# Functions & classes =========================================================
def _read_template():
    with open(INDEX_PATH) as f:
        return f.read()


def render_registered(remote_info):
    template = _read_template()

    return template


def render_unregistered():
    return "unregistered"


def get_remote_info(url_id):  # TODO: Add timeout, print error in case of exception
    resp = requests.get(settings.REMOTE_INFO_URL)
    resp.raise_for_status()
    data = resp.json()

    assert "url" in data

    return data


# TODO: REMOVE
@get("/" + settings.REMOTE_INFO_URL.split("/")[-1])
def mock_data():
    return {
        "url": "http://seznam.cz",
    }
# TODO: REMOVE


@get("/<fn:path>")
def static_data(fn):
    file_path = os.path.normpath(fn)
    full_path = os.path.join(STATIC_PATH, file_path)

    if not os.path.exists(full_path):
        abort(404, "'%s' not found!" % fn)

    return static_file(
        file_path,
        STATIC_PATH
    )


@get("/")
def render_form_template():
    url_id = request.query.get("url_id", None)

    registered_user = False
    if url_id is not None:
        remote_info = get_remote_info(url_id)
        registered_user = True

    if registered_user:
        return render_registered(remote_info)

    return render_unregistered()
