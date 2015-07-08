#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests
from bottle import get
from bottle import request

from . import settings


# Functions & classes =========================================================
def render_registered(remote_info):
    return "registered"


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
