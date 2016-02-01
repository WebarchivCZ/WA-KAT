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
    """
    This class represents input mapper for the Conspect and Subconspect values.

    Class handles both Select elements in HTML and typeahead input and defines
    high-level access to them.
    """
    conspect = {}
    conspect_to_id = {}

    input_el = document["conspect_subconspect"]
    conspect_el = document["konspekt"]
    subconspect_el = document["subkonspekt"]

    value = None
    is_twoconspect = True

    @classmethod
    def _save_value(cls):
        """
        Callback used to automatically store value in :attr:`value` property
        each time the user selects value.
        """
        consp = min(sel.value for sel in cls.conspect_el if sel.selected)
        sub = min(sel.value for sel in cls.subconspect_el if sel.selected)

        cls.value = cls.conspect[consp][sub]

    @classmethod
    def _set_sub_conspect(cls):
        """
        Look at the :attr:`conspect_el` and put proper subconspect values into
        subconspect's  <select> element.

        Also bind the :meth:`_save_value` for user changes.
        """
        selected = min(sel.value for sel in cls.conspect_el if sel.selected)

        cls.subconspect_el.html = ""

        for key in sorted(cls.conspect[selected].keys()):
            cls.subconspect_el <= html.OPTION(key, value=key)

        cls.subconspect_el.bind('change', lambda x: cls._save_value())

    @classmethod
    def _create_searchable_typeahead(cls):
        """
        Create typeahead <input> element and fill it with data.
        """
        window.destroy_typeahead_tag("#conspect_subconspect_typeahead")
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
    def set_new_conspect_dict(cls, conspect, conspect_to_id):
        """
        In case that new conspect dict was retreived (by analysis for example),
        update it's values.

        This method also initializes the HTML elements (both <select> and
        typeahead, so it may be good thing to call it somewhere in constructor.

        Args:
            conspect (dict): New ``{conspect: {subconspect: code}`` mapping.
            conspect_to_id (dict): Reverse ``{conspect: ID}`` code mapping.
        """
        cls.conspect = conspect
        cls.conspect_to_id = conspect_to_id

        cls.conspect_el.html = ""
        for key in sorted(cls.conspect.keys()):
            cls.conspect_el <= html.OPTION(key, value=key)

        cls.conspect_el.bind('change', lambda x: cls._set_sub_conspect())

        cls._create_searchable_typeahead()

    @classmethod
    def _get_sub_to_code_mapping(cls):
        """
        Create and return subconspect: code dictionary.

        Returns:
            dict: ``{subconspect: code}``
        """
        subconspects_list = [
            list(subconspect_dict.items())
            for subconspect_dict in cls.conspect.values()
        ]
        subconspects_list = sum(subconspects_list, [])  # flattern
        return dict(subconspects_list)

    @classmethod
    def _get_sub_to_consp_mapping(cls):
        """
        Create and return subconspect: conspect dictionary.

        Returns:
            dict: ``{subconspect: conspect}``
        """
        sub_to_consp = [
            [(subconsp_name, consp) for subconsp_name in subconsp.keys()]
            for consp, subconsp in cls.conspect.items()
        ]
        sub_to_consp = sum(sub_to_consp, [])  # flattern
        return dict(sub_to_consp)

    @classmethod
    def _find_code_by_sub(cls, subconspect):
        """
        Look into :meth:`_get_sub_to_code_mapping` dict and find code for given
        `subconspect`.

        Returns:
            str: Conspect/subconspect code.
        """
        return cls._get_sub_to_code_mapping()[subconspect]

    @classmethod
    def _find_sub_by_code(cls, code):
        """
        Look into :meth:`_get_sub_to_code_mapping` dict and find subconspect
        for given `code`.

        Returns:
            str: Subconspect value for given code.
        """
        reversed_sub = {
            val: key
            for key, val in cls._get_sub_to_code_mapping().items()
        }

        return reversed_sub[code]

    @classmethod
    def get(cls):
        """
        Get code selected by user.

        Returns:
            str: Code or None in case that user didn't selected anything yet.
        """
        if cls.is_twoconspect:
            return cls.value

        sub = cls.input_el.value

        # blank user input -> no value was yet set
        if not sub.strip():
            return None

        sub_to_code_dict = cls._get_sub_to_code_mapping()

        if sub not in sub_to_code_dict:
            alert("Invalid sub-conspect `%s`!" % sub)

        return sub_to_code_dict[sub]

    @classmethod
    def get_dict(cls):
        code = cls.get()

        sub = cls._find_sub_by_code(code)
        conspect = cls._get_sub_to_consp_mapping()[sub]

        return {
            "sub_code": code,
            "sub_name": cls._find_sub_by_code(code),
            "consp_id": cls.conspect_to_id[conspect],
        }

    @classmethod
    def set(cls, code):
        """
        Set value for <input> / <select> tags based on code.

        Args:
            code (str): Code of the conspect / subconspect.
        """
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
            cls.value = code
        else:
            cls.input_el.value = sub_val

    @classmethod
    def bind_switcher(cls):
        """
        Bind the switch checkbox to functions for switching between types of
        inputs.
        """
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
            val = cls.get()

            for el in document.get(selector=".conspect_switcher"):
                el.checked = ev.target.checked

            if document.get(selector=".conspect_switcher")[0].checked:
                hide_two_conspect()
                cls.set(val)
                return

            show_two_conspect()
            cls.set(val)

        for el in document.get(selector=".conspect_switcher"):
            el.bind("change", show_or_hide_two_conspect)


ConspectHandler.bind_switcher()
