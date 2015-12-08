#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import html
from browser import window
from browser import document


# Functions & classes =========================================================
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
    def set_conspect(cls, new_conspect):
        cls.conspect = new_conspect

        cls.conspect_el.html = ""
        for key in sorted(cls.conspect.keys()):
            cls.conspect_el <= html.OPTION(key)

        cls.conspect_el.bind('change', lambda x: cls._set_sub_conspect())

        cls._create_searchable_typeahead()
