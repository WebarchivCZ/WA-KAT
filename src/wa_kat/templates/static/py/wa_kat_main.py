#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import time

from browser import ajax
from browser import alert  # TODO: Remove
from browser import document


# GUI views ===================================================================
class UrlBoxError(object):
    def __init__(self):
        self.hide()

    def show(self, msg):
        document["urlbox_error"].innerHTML = msg
        document["whole_urlbox_error"].style.display = "block"

    def hide(self):
        document["whole_urlbox_error"].style.display = "none"


class ProgressBar(object):
    def __init__(self):
        # self.hide()
        pass

    def _compute_percentage(self, progress_tuple):
        return (100 / progress_tuple[1]) * progress_tuple[0]

    def show(self, progress, msg=None):
        if document["whole_progress_bar"].style.display == "none":
            document["whole_progress_bar"].style.display = "block"

        percentage = str(self._compute_percentage(progress))
        document["progress_bar"].aria_valuemin = percentage
        document["progress_bar"].style.width = "{}%".format(percentage)

        if msg:
            document["progress_bar"].innerHTML = msg

    def hide(self):
        document["whole_progressbar"].style.display = "none"


# Variables ===================================================================
URL_BOX_ERROR = UrlBoxError()
PROGRESS_BAR = ProgressBar()


# Functions & classes =========================================================
def fill_inputs(values):
    alert(values)


def on_complete(req):
    # handle http errors
    if not (req.status == 200 or req.status == 0):
        URL_BOX_ERROR.show(req.text)
        return

    resp = json.loads(req.text)

    # handle structured errors
    if not resp["status"]:
        URL_BOX_ERROR.show(resp["error"])
        return

    # keep tracking of the progress
    if not resp["body"]["all_set"]:
        PROGRESS_BAR.show(resp["body"]["progress"])
        time.sleep(0.5)
        make_request(document["url"].value)
        return

    # finally save the data to inputs
    PROGRESS_BAR.show(resp["body"]["progress"])
    fill_inputs(resp["body"]["values"])


def make_request(url):
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', "/api_v1/analyze", True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send({'url': url})


def start_analysis(ev):
    url = document["url"].value.strip()

    # make sure, that `url` was filled in
    if not url.strip():
        URL_BOX_ERROR.show("URL musí být vyplněna.")
        return

    URL_BOX_ERROR.hide()

    # normalize the `url`
    if not (url.startswith("http://") or url.startswith("http://")):
        url = "http://" + url
        document["url"].value = url  # store normalized url back to input

    make_request(url)


document["run_button"].bind("click", start_analysis)
