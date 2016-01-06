#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple

from browser import html
from browser import window
from browser import document


# Functions & classes =========================================================
class ConspectVal(namedtuple("ConspectVal", ["conspect", "subconspect"])):
    pass


class ConspectHandler(object):
    conspect = {}
    conspect_el = document["konspekt"]
    subconspect_el = document["subkonspekt"]
    value = None

    @classmethod
    def _save_value(cls):
        consp = min(sel.value for sel in cls.conspect_el if sel.selected)
        sub = min(sel.value for sel in cls.subconspect_el if sel.selected)

        cls.value = cls.conspect[consp][sub]

    @classmethod
    def _set_sub_conspect(cls):
        selected = min(sel.value for sel in cls.conspect_el if sel.selected)

        cls.subconspect_el.html = ""

        for key in sorted(cls.conspect[selected].keys()):
            cls.subconspect_el <= html.OPTION(key)

        cls.subconspect_el.bind('change', lambda x: cls._save_value())

    @classmethod
    def _create_searchable_typeahead(cls):
        args = [
            {
                "name": key,
                "data": sorted(cls.conspect[key].keys()),
            }
            for key in sorted(cls.conspect.keys())
        ]
        window.make_multi_searchable_typeahead_tag(
            "#conspect_subconspect_typeahead",
            *args
        )

    @classmethod
    def set_new_conspect_dict(cls, new_conspect):
        cls.conspect = new_conspect

        cls.conspect_el.html = ""
        for key in sorted(cls.conspect.keys()):
            cls.conspect_el <= html.OPTION(key)

        cls.conspect_el.bind('change', lambda x: cls._set_sub_conspect())

        cls._create_searchable_typeahead()

    @classmethod
    def get(cls):
        raise NotImplementedError("Not implemented yet!")  # TODO: implement

    @classmethod
    def set(cls, val):
        raise NotImplementedError("Not implemented yet!")  # TODO: implement

    @staticmethod
    def bind_switcher():
        def show_two_conspect():
            for el in document.get(selector=".two_conspect"):
                el.style.display = "block"

            for el in document.get(selector=".searchable_conspect"):
                el.style.display = "none"

        def hide_two_conspect():
            for el in document.get(selector=".two_conspect"):
                el.style.display = "none"

            for el in document.get(selector=".searchable_conspect"):
                el.style.display = "block"

        def show_or_hide_two_conspect(ev):
            for el in document.get(selector=".conspect_switcher"):
                el.checked = ev.target.checked

            if document.get(selector=".conspect_switcher")[0].checked:
                return hide_two_conspect()

            return show_two_conspect()

        for el in document.get(selector=".conspect_switcher"):
            el.bind("change", show_or_hide_two_conspect)
