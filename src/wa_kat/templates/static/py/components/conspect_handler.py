#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import html
from browser import alert
from browser import window
from browser import document


# Functions & classes =========================================================
class ConspectHandler(object):
    conspect = {}

    input_el = document["conspect_subconspect"]
    conspect_el = document["konspekt"]
    subconspect_el = document["subkonspekt"]

    value = None
    is_twoconspect = True

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
            cls.subconspect_el <= html.OPTION(key, value=key)

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
            cls.conspect_el <= html.OPTION(key, value=key)

        cls.conspect_el.bind('change', lambda x: cls._set_sub_conspect())

        cls._create_searchable_typeahead()

    @classmethod
    def _get_sub_to_code_mapping(cls):
        subconspects_list = [
            list(subconspect_dict.items())
            for subconspect_dict in cls.conspect.values()
        ]
        subconspects_list = sum(subconspects_list, [])  # flattern
        return dict(subconspects_list)

    @classmethod
    def _get_sub_to_consp_mapping(cls):
        sub_to_consp = [
            [(subconsp_name, consp) for subconsp_name in subconsp.keys()]
            for consp, subconsp in cls.conspect.items()
        ]
        sub_to_consp = sum(sub_to_consp, [])  # flattern
        return dict(sub_to_consp)

    @classmethod
    def _find_code_by_sub(cls, subconspect):
        return cls._get_sub_to_code_mapping()[subconspect]

    @classmethod
    def _find_sub_by_code(cls, code):
        reversed_sub = {
            val: key
            for key, val in cls._get_sub_to_code_mapping().items()
        }

        return reversed_sub[code]

    @classmethod
    def get(cls):
        if cls.is_twoconspect:
            return cls.value

        sub = cls.input_el.value
        sub_to_code_dict = cls._get_sub_to_code_mapping()

        if sub not in sub_to_code_dict:
            alert("Invalid sub-conspect `%s`!" % sub)

        return sub_to_code_dict[sub]

    @classmethod
    def set(cls, code):
        if type(code) in [list, tuple]:
            code = code[0]

        if isinstance(code, dict):
            code = code["val"]

        sub_val = cls._find_sub_by_code(code)
        if cls.is_twoconspect:
            sub_to_consp_dict = cls._get_sub_to_consp_mapping()

            if sub_val not in sub_to_consp_dict:
                return

            konsp_val = sub_to_consp_dict[sub_val]
            cls.conspect_el.value = konsp_val
            cls._set_sub_conspect()
            cls.subconspect_el.value = sub_val
        else:
            cls.input_el.value = sub_val

    @classmethod
    def bind_switcher(cls):
        def show_two_conspect():
            cls.is_twoconspect = True

            for el in document.get(selector=".two_conspect"):
                el.style.display = "block"

            for el in document.get(selector=".searchable_conspect"):
                el.style.display = "none"

        def hide_two_conspect():
            cls.is_twoconspect = False

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
