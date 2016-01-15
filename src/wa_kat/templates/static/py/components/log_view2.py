#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import document


# Functions & classes =========================================================
class LogView(object):
    _value = []
    el = document["log_placeholder"]
    black_overlay = document["black_overlay"]
    show_button = document["show_log"]

    @classmethod
    def _render(cls):
        cls.el.innerHTML = cls.get()

    @classmethod
    def set(cls, msg):
        cls._value.append(msg)
        cls._render()

    @classmethod
    def get(cls):
        return "\n".join(cls._value)

    @classmethod
    def show(cls, msg=None):
        if msg:
            cls.set(msg)

        cls.el.style.display = "block"
        cls.black_overlay.style.display = "block"

    @classmethod
    def hide(cls):
        cls.el.style.display = "none"
        cls.black_overlay.style.display = "none"

    @classmethod
    def bind(cls):
        cls.black_overlay.bind("click", lambda ev: cls.hide())
        cls.show_button.bind("click", lambda ev: cls.show())


LogView.bind()
LogView.show("hello")
