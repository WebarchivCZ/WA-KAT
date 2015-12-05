#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import document


# Functions & classes =========================================================
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
