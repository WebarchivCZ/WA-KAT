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
    tag = document["urlbox_error"]
    whole_tag = document["whole_urlbox_error"]

    @classmethod
    def show(cls, msg):
        cls.tag.innerHTML = msg
        cls.whole_tag.style.display = "block"

    @classmethod
    def hide(cls):
        cls.whole_tag.style.display = "none"

    @classmethod
    def reset(cls):
        cls.hide()
        cls.tag.innerHTML = ""


class ProgressBar(object):
    tag = document["progress_bar"]
    whole_tag = document["whole_progress_bar"]
    original_message = tag.text

    @staticmethod
    def _compute_percentage(progress_tuple):
        # division by zero..
        if progress_tuple[0] == 0:
            return 0

        return (100 / progress_tuple[1]) * progress_tuple[0]

    @classmethod
    def show(cls, progress, msg=None):
        if cls.whole_tag.style.display == "none":
            cls.whole_tag.style.display = "block"

        percentage = cls._compute_percentage(progress)

        # toggle animation
        cls.tag.class_name = "progress-bar"
        if percentage < 100:
            cls.tag.class_name += " progress-bar-striped active"
        else:
            msg = "Hotovo"

        # show percentage in progress bar
        cls.tag.aria_valuemin = percentage
        cls.tag.style.width = "{}%".format(percentage)

        if msg:
            cls.tag.text = msg

    @classmethod
    def hide(cls):
        cls.whole_tag.style.display = "none"

    @classmethod
    def reset(cls):
        cls.hide()
        cls.tag.class_name = "progress-bar progress-bar-striped active"
        cls.tag.aria_valuemin = 0
        cls.tag.style.width = "{}%".format(0)
        cls.tag.text = cls.original_message


class DropdownHandler(object):
    @staticmethod
    def _get_dropdown_glyph_el(input_id):
        input_el = document[input_id]
        parent = input_el.parent
        grand_parent = parent.parent

        for el in list(parent.children) + list(grand_parent.children):
            if el.class_name and "dropdown_hint" in el.class_name.lower():
                return el

        raise ValueError("Dropdown not found!")

    @classmethod
    def show_dropdown_glyph(cls, input_id):
        el = cls._get_dropdown_glyph_el(input_id)
        el.style.display = "block"

        return el

    @classmethod
    def hide_dropdown_glyph(cls, input_id):
        el = cls._get_dropdown_glyph_el(input_id)
        el.style.display = "none"

        return el

    @classmethod
    def set_dropdown_glyph(cls, input_id, glyph_name):
        el = cls.show_dropdown_glyph(input_id)
        filtered_tokens = [
            token
            for token in str(el.class_name).split()
            if "glyphicon" not in token
        ]
        tokens = filtered_tokens + ["glyphicon", glyph_name]

        el.class_name = " ".join(tokens)
        return el


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
    _dropdown_text = " Klikněte pro výběr."

    @classmethod
    def _get_el(cls, rest_id):
        return document[cls._map[rest_id]]

    @staticmethod
    def set_placeholder_text(input_el, text):
        input_el.placeholder = text

    @staticmethod
    def get_placeholder_text(input_el):
        return input_el.placeholder

    @classmethod
    def set_placeholder_dropdown(cls, input_el):
        text = cls.get_placeholder_text(input_el)
        cls.set_placeholder_text(
            input_el=input_el,
            text=text + cls._dropdown_text
        )

    @classmethod
    def reset_placeholder_dropdown(cls, input_el):
        text = cls.get_placeholder_text(input_el)
        cls.set_placeholder_text(
            input_el=input_el,
            text=text.replace(cls._dropdown_text, "")
        )

    @classmethod
    def _set_typeahead(cls, key, el, value):
        cls.reset_placeholder_dropdown(el)

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
        cls.set_placeholder_dropdown(el)
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


# Functions ===================================================================
def on_complete(req):
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
        make_request(document["url"].value)
        return

    # finally save the data to inputs
    ProgressBar.show(resp["body"]["progress"])
    InputMapper.fill_inputs(resp["body"]["values"])


def make_request(url):
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', "/api_v1/analyze", True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send({'url': url})


def start_analysis(ev):
    # reset all inputs
    ProgressBar.reset()
    ProgressBar.show([0, 0])
    InputMapper.reset()
    UrlBoxError.reset()

    # read the urlbox
    url = document["url"].value.strip()

    # make sure, that `url` was filled in
    if not url.strip():
        UrlBoxError.show("URL musí být vyplněna.")
        return

    UrlBoxError.hide()

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
