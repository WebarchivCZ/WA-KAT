#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json

from browser import ajax
from browser import alert  # TODO: Remove
from browser import document


# Variables ===================================================================
# Functions & classes =========================================================
def show_url_box_error(msg):
    document["urlbox_error"].innerHTML = msg
    document["whole_urlbox_error"].style.display = "block"


def hide_url_box_error():
    document["whole_urlbox_error"].style.display = "none"


def fill_inputs(values):
    alert(values)


def show_progress(progress):
    pass


def on_complete(req):
    if not (req.status == 200 or req.status == 0):
        show_url_box_error(req.text)
        return

    resp = json.loads(req.text)

    if not resp["status"]:
        show_url_box_error(resp["error"])
        return

    if not resp["body"]["all_set"]:
        show_progress(resp["body"]["progress"])
        make_request(document["url"].value)
        return

    show_progress(resp["body"]["progress"])
    fill_inputs(resp["body"]["values"])


def make_request(url):
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', "/api_v1/analyze", True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send({'url': url})


def start_analysis(ev):
    url = document["url"].value.strip()

    if not url.strip():
        show_url_box_error("URL musí být vyplněna.")
        return

    hide_url_box_error()

    if not (url.startswith("http://") or url.startswith("http://")):
        url = "http://" + url
        document["url"].value = url

    make_request(url)


document["run_button"].bind("click", start_analysis)
