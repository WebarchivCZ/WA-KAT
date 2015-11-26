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
        self.tag = document["urlbox_error"]
        self.whole_tag = document["whole_urlbox_error"]

    def show(self, msg):
        self.tag.innerHTML = msg
        self.whole_tag.style.display = "block"

    def hide(self):
        self.whole_tag.style.display = "none"


class ProgressBar(object):
    def __init__(self):
        self.tag = document["progress_bar"]
        self.whole_tag = document["whole_progress_bar"]

    def _compute_percentage(self, progress_tuple):
        return (100 / progress_tuple[1]) * progress_tuple[0]

    def show(self, progress, msg=None):
        if self.whole_tag.style.display == "none":
            self.whole_tag.style.display = "block"

        percentage = self._compute_percentage(progress)

        # toggle animation
        if percentage < 100:
            self.tag.class_name = "progress-bar progress-bar-striped active"
        else:
            self.tag.class_name = "progress-bar"
            msg = "Hotovo"

        # show percentage in progress bar
        self.tag.aria_valuemin = percentage
        self.tag.style.width = "{}%".format(percentage)

        if msg:
            self.tag.text = msg

    def hide(self):
        self.whole_tag.style.display = "none"


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


def analysis_after_enter_pressed(ev):
    ev.stopPropagation()

    if ev.keyCode == 13:
        start_analysis(ev)


document["run_button"].bind("click", start_analysis)
document["url"].bind("keypress", analysis_after_enter_pressed)
