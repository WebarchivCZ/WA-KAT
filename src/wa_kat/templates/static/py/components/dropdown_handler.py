#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import document


# Functions & classes =========================================================
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
