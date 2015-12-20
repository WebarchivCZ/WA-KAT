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

from components import ProgressBar
from components import UrlBoxError
from components import ISSNBoxError
from components import ConspectHandler
from components import DropdownHandler
from components import PlaceholderHandler


# GUI views ===================================================================
class InputMapper(object):
    _map = {  # TODO: get rid of this
        "title_tags": "title",
        "place_tags": "place",
        "lang_tags": "lang",
        "keyword_tags": "keywords",
        "author_tags": "author",
        "annotation_tags": "annotation",
        "creation_dates": "creation_date",
    }
    _set_by_typeahead = set()

    @classmethod
    def _get_el(cls, rest_id):
        return document[cls._map[rest_id]]

    @classmethod
    def _set_typeahead(cls, key, el, value):
        PlaceholderHandler.reset_placeholder_dropdown(el)

        # if there is no elements, show alert icon in glyph
        if not value:
            DropdownHandler.set_dropdown_glyph(el.id, "glyphicon-alert")
            return

        # if there is only one element, don't use typeahead, just put the
        # information to the input, set different dropdown glyph and put source
        # to the dropdown
        if len(value) == 1:
            source = value[0]["source"].strip()
            dropdown_el = DropdownHandler.set_dropdown_glyph(
                el.id,
                "glyphicon-eye-open"
            )
            dropdown_content = "<span class='gray_text'>&nbsp;(%s)</span>"

            # save the source to the dropdown menu
            if source:
                dropdown_el.html = dropdown_content % source[::-1]

            el.value = value[0]["val"]
            return

        # get reference to parent element
        parent_id = el.parent.id
        if "typeahead" not in parent_id.lower():
            parent_id = el.parent.parent.id

        # if there are multiple elements, put them to the typeahead and show
        # dropdown glyph
        window.make_typeahead_tag("#" + parent_id, value)
        DropdownHandler.set_dropdown_glyph(el.id, "glyphicon-menu-down")
        PlaceholderHandler.set_placeholder_dropdown(el)
        cls._set_by_typeahead.add(parent_id)

    @staticmethod
    def _set_input(key, el, value):
        el.value = ", ".join(item.val for item in value)

    @staticmethod
    def _set_textarea(key, el, value):
        el.text = "\n\n".join(
            "-- %s --\n%s" % (item["source"], item["val"])
            for item in value
        )

    @classmethod
    def map(cls, key, value):
        if key == "conspect":
            return ConspectHandler.set_conspect(value)

        el = cls._get_el(key)
        tag_name = el.elt.tagName.lower()

        if tag_name == "textarea":
            cls._set_textarea(key, el, value)
        elif tag_name == "input":
            if "typeahead" in el.class_name.lower():
                cls._set_typeahead(key, el, value)
            else:
                cls._set_input(key, el, value)
        elif tag_name == "select":
            pass  # TODO: implement selecting of the keywords
        else:
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )

    @classmethod
    def fill_inputs(cls, values):
        for key, value in values.items():
            cls.map(key, value)

    @classmethod
    def reset(cls):
        for el_id in cls._set_by_typeahead:
            window.destroy_typyahead_tag("#" + el_id)

        cls._set_by_typeahead = set()


# Background processes ========================================================
class AnalysisRunner(object):
    @classmethod
    def on_complete(cls, req):
        # handle http errors
        if not (req.status == 200 or req.status == 0):
            UrlBoxError.show(req.text)
            return

        resp = json.loads(req.text)

        # handle structured errors
        if not resp["status"]:
            UrlBoxError.show(resp["error"])
            return

        # keep tracking of the progress
        if not resp["body"]["all_set"]:
            ProgressBar.show(resp["body"]["progress"])
            time.sleep(0.5)
            make_request(
                url="/api_v1/analyze",
                data={'url': document["url"].value},
                on_complete=cls.on_complete,
            )
            return

        # finally save the data to inputs
        ProgressBar.show(resp["body"]["progress"])
        InputMapper.fill_inputs(resp["body"]["values"])

    @classmethod
    def start(cls, ev):
        # reset all inputs
        ProgressBar.reset()
        ProgressBar.show([0, 0])
        InputMapper.reset()
        UrlBoxError.reset()

        # read the urlbox
        url = document["url"].value.strip()

        # make sure, that `url` was filled in
        if not url:
            UrlBoxError.show("URL musí být vyplněna.")
            return

        UrlBoxError.hide()

        # normalize the `url`
        if not (url.startswith("http://") or url.startswith("http://")):
            url = "http://" + url
            document["url"].value = url  # store normalized url back to input

        make_request(
            url="/api_v1/analyze",
            data={'url': url},
            on_complete=cls.on_complete
        )


class AlephReader(object):
    @classmethod
    def on_complete(cls, req):
        # handle http errors
        if not (req.status == 200 or req.status == 0):
            UrlBoxError.show(req.text)
            return

        resp = json.loads(req.text)

        if not resp:
            ISSNBoxError.show("Pro zadané ISSN nebyly nalezeny žádná data.")
            return

        alert(resp)

    @classmethod
    def start(cls, ev):
        # reset all inputs
        # InputMapper.reset()  # TODO: 
        ISSNBoxError.reset()

        # read the urlbox
        issn = document["issn"].value.strip()

        # make sure, that `url` was filled in
        if not issn:
            ISSNBoxError.show("ISSN nebylo vyplněno!")
            return

        ISSNBoxError.hide()

        make_request(
            url="/api_v1/aleph",
            data={'issn': issn},
            on_complete=cls.on_complete
        )


# Functions ===================================================================
def make_request(url, data, on_complete):
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', url, True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send(data)


def function_on_enter(func):
    def function_after_enter_pressed(ev):
        ev.stopPropagation()

        # if the key was `enter` ..
        if ev.keyCode == 13:
            func(ev)

    return function_after_enter_pressed


document["run_button"].bind("click", AnalysisRunner.start)
document["url"].bind("keypress", function_on_enter(AnalysisRunner.start))
document["issn_run_button"].bind("click", AlephReader.start)
document["issn"].bind("keypress", function_on_enter(AlephReader.start))
ConspectHandler.bind_switcher()

# AnalysisRunner.start(1)
