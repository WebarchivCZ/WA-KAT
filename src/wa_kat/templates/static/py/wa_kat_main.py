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

    @staticmethod
    def show(msg):
        UrlBoxError.tag.innerHTML = msg
        UrlBoxError.whole_tag.style.display = "block"

    @staticmethod
    def hide():
        UrlBoxError.whole_tag.style.display = "none"

    @staticmethod
    def reset():
        UrlBoxError.hide()
        UrlBoxError.tag.innerHTML = ""


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

    @staticmethod
    def show(progress, msg=None):
        if ProgressBar.whole_tag.style.display == "none":
            ProgressBar.whole_tag.style.display = "block"

        percentage = ProgressBar._compute_percentage(progress)

        # toggle animation
        ProgressBar.tag.class_name = "progress-bar"
        if percentage < 100:
            ProgressBar.tag.class_name += " progress-bar-striped active"
        else:
            msg = "Hotovo"

        # show percentage in progress bar
        ProgressBar.tag.aria_valuemin = percentage
        ProgressBar.tag.style.width = "{}%".format(percentage)

        if msg:
            ProgressBar.tag.text = msg

    @staticmethod
    def hide():
        ProgressBar.whole_tag.style.display = "none"

    @staticmethod
    def reset():
        ProgressBar.hide()
        ProgressBar.tag.class_name = "progress-bar progress-bar-striped active"
        ProgressBar.tag.aria_valuemin = 0
        ProgressBar.tag.style.width = "{}%".format(0)
        ProgressBar.tag.text = ProgressBar.original_message


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

    @staticmethod
    def show_dropdown_glyph(input_id):
        el = DropdownHandler._get_dropdown_glyph_el(input_id)
        el.style.display = "block"

        return el

    @staticmethod
    def hide_dropdown_glyph(input_id):
        el = DropdownHandler._get_dropdown_glyph_el(input_id)
        el.style.display = "none"

        return el

    @staticmethod
    def set_dropdown_glyph(input_id, glyph_name):
        el = DropdownHandler.show_dropdown_glyph(input_id)
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

    @staticmethod
    def _get_el(rest_id):
        return document[InputMapper._map[rest_id]]

    @staticmethod
    def set_placeholder_text(input_el, text):
        input_el.placeholder = text

    @staticmethod
    def get_placeholder_text(input_el):
        return input_el.placeholder

    @staticmethod
    def set_placeholder_dropdown(input_el):
        text = InputMapper.get_placeholder_text(input_el)
        InputMapper.set_placeholder_text(
            input_el=input_el,
            text=text + InputMapper._dropdown_text
        )

    @staticmethod
    def reset_placeholder_dropdown(input_el):
        text = InputMapper.get_placeholder_text(input_el)
        InputMapper.set_placeholder_text(
            input_el=input_el,
            text=text.replace(InputMapper._dropdown_text, "")
        )

    @staticmethod
    def _set_typeahead(key, el, value):
        InputMapper.reset_placeholder_dropdown(el)

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
        InputMapper.set_placeholder_dropdown(el)
        InputMapper._set_by_typeahead.add(parent_id)

    @staticmethod
    def _set_input(key, el, value):
        el.value = ", ".join(item.val for item in value)

    @staticmethod
    def _set_textarea(key, el, value):
        el.text = "\n\n".join(
            "-- %s --\n%s" % (item["source"], item["val"])
            for item in value
        )

    @staticmethod
    def map(key, value):
        el = InputMapper._get_el(key)
        tag_name = el.elt.tagName.lower()

        if tag_name == "textarea":
            InputMapper._set_textarea(key, el, value)
        elif tag_name == "input":
            if "typeahead" in el.class_name.lower():
                InputMapper._set_typeahead(key, el, value)
            else:
                InputMapper._set_input(key, el, value)
        elif tag_name == "select":
            pass  # TODO: implement selecting of the keywords
        else:
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )

    @staticmethod
    def fill_inputs(values):
        for key, value in values.items():
            InputMapper.map(key, value)

    @staticmethod
    def reset():
        for el_id in InputMapper._set_by_typeahead:
            window.destroy_typyahead_tag("#" + el_id)

        InputMapper._set_by_typeahead = set()


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
