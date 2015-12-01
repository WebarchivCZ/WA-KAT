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
from browser import window
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

    def reset(self):
        self.hide()
        self.tag.innerHTML = ""


class ProgressBar(object):
    def __init__(self):
        self.tag = document["progress_bar"]
        self.whole_tag = document["whole_progress_bar"]
        self.original_message = self.tag.text

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

    def reset(self):
        self.hide()
        self.tag.class_name = "progress-bar progress-bar-striped active"
        self.tag.aria_valuemin = 0
        self.tag.style.width = "{}%".format(0)
        self.tag.text = self.original_message


class InputMapper(object):
    def __init__(self):
        self._map = {  # TODO: get rid of this
            "title_tags": "title",
            "place_tags": "place",
            "lang_tags": "lang",
            "keyword_tags": "keywords",
            "author_tags": "author",
            "annotation_tags": "annotation",
            "creation_dates": "creation_date",
        }
        self.typeahead_set = set()

    def _get_el(self, rest_id):
        return document[self._map[rest_id]]

    def _set_typeahead(self, key, el, value):
        parent_id = el.parent.id
        if "typeahead" not in parent_id.lower():
            parent_id = el.parent.parent.id

        window.make_typeahead_tag("#" + parent_id, value)
        self.typeahead_set.add(parent_id)

    def _set_input(self, key, el, value):
        el.value = ", ".join(item.val for item in value)

    def _set_textarea(self, key, el, value):
        el.text = "\n\n--\n\n".join(item.val for item in value)

    def map(self, key, value):
        el = self._get_el(key)
        tag_name = el.elt.tagName.lower()

        if tag_name == "textarea":  # TODO: handle case when there already is something
            self._set_textarea(key, el, value)
        elif tag_name == "input":  # použít tag it
            if "typeahead" in el.class_name.lower():
                self._set_typeahead(key, el, value)
            else:
                self._set_input(key, el, value)
        else:
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )

    def fill_inputs(self, values):
        for key, value in values.items():
            self.map(key, value)

    def reset(self):
        for el_id in self.typeahead_set:
            window.destroy_typyahead_tag("#" + el_id)

        self.typeahead_set = set()


# Variables ===================================================================
URL_BOX_ERROR = UrlBoxError()
PROGRESS_BAR = ProgressBar()
INPUT_MAPPER = InputMapper()


# Functions & classes =========================================================
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
    INPUT_MAPPER.fill_inputs(resp["body"]["values"])


def make_request(url):
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', "/api_v1/analyze", True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send({'url': url})


def start_analysis(ev):
    # reset all inputs
    PROGRESS_BAR.reset()
    INPUT_MAPPER.reset()
    URL_BOX_ERROR.reset()

    # read the urlbox
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

    # if the key was `enter` ..
    if ev.keyCode == 13:
        start_analysis(ev)


document["run_button"].bind("click", start_analysis)
document["url"].bind("keypress", analysis_after_enter_pressed)
