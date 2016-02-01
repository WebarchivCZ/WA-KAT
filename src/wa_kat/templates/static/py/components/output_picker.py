#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import base64

from browser import document

from .log_view2 import LogView


# Variables ===================================================================
# Functions & classes =========================================================
class OutputPicker(object):
    el = document["output_picker"]
    black_overlay = LogView.black_overlay

    mrc_out_el = document["mrc_output"]
    oai_out_el = document["marc_oai_output"]
    dc_out_el = document["dublin_core_output"]

    values = None
    filename = "fn"

    @classmethod
    def set(cls, values):
        cls.mrc_out_el.text = values.get("mrc", "")
        cls.oai_out_el.text = values.get("oai", "")
        cls.dc_out_el.text = values.get("dc", "")
        cls.filename = values.get("fn", "fn")

        cls.values = values

    @classmethod
    def show(cls, values=None):
        if values:
            cls.set(values)

        cls.el.style.display = "block"
        cls.black_overlay.style.display = "block"
        cls.bind()

    @classmethod
    def hide(cls):
        cls.el.style.display = "none"
        cls.black_overlay.style.display = "none"

    @classmethod
    def bind(cls):
        cls.black_overlay.bind("click", lambda ev: cls.hide())

    @classmethod
    def bind_download_buttons(cls):
        def on_click(ev):
            button_el = ev.target
            form_el = button_el.parent.parent.parent

            # this allows to use disabled <textearea>, which is normally not
            # sent
            content = form_el.get(selector="textarea")[0].text

            # change filename according to output
            suffix = form_el.name
            form_el.action = "/api_v1/as_file/%s.%s" % (cls.filename, suffix)

            input_el = form_el.get(selector="input")[0]
            input_el.value = content

        for el in document.get(selector="button.output_download_button"):
            el.bind("click", on_click)


OutputPicker.bind_download_buttons()
