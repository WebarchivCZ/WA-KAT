#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import alert  # TODO: Remove

from browser import window
from browser import document

from components import LogView
from components import ProgressBar
from components import UrlBoxError
from components import ISSNBoxError
from components import ConspectHandler
from components import DropdownHandler
from components import PlaceholderHandler
from components import UserKeywordHandler
from components import AlephKeywordHandler
from components import AanalysisKeywordHandler


# Functions & classes =========================================================
class InputController(object):
    # this is used to track what kind of elements were added by typeahead
    _set_by_typeahead = set()

    @staticmethod
    def _set_input(el, value):
        """
        Set content of given `el` to `value`.

        Args:
            el (obj): El reference to input you wish to set.
            value (obj/list): Value to which the `el` will be set.
        """
        if isinstance(value, dict):
            el.value = value["val"]
        elif type(value) in [list, tuple]:
            el.value = ", ".join(item["val"] for item in value)
        else:
            el.value = value

    @staticmethod
    def _set_textarea(el, value):
        """
        Set content of given textarea element `el` to `value`.

        Args:
            el (obj): Reference to textarea element you wish to set.
            value (obj/list): Value to which the `el` will be set.
        """
        if isinstance(value, dict):
            el.text = value["val"]
        elif type(value) in [list, tuple]:
            el.text = "\n\n".join(
                "-- %s --\n%s" % (item["source"], item["val"])
                for item in value
            )
        else:
            el.text = value

    @classmethod
    def _set_typeahead(cls, el, value):
        """
        Convert given `el` to typeahead input and set it to `value`.

        This method also sets the dropdown icons and descriptors.

        Args:
            el (obj): Element reference to the input you want to convert to
                typeahead.
            value (list): List of dicts with two keys: ``source`` and ``val``.
        """
        PlaceholderHandler.reset_placeholder_dropdown(el)

        # if there is no elements, show alert icon in glyph
        if not value and not el.value:
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

        # TODO: preserve old values
        if parent_id in cls._set_by_typeahead:
            window.destroy_typeahead_tag("#" + parent_id)

        # if there are multiple elements, put them to the typeahead and show
        # dropdown glyph
        window.make_typeahead_tag("#" + parent_id, value)
        DropdownHandler.set_dropdown_glyph(el.id, "glyphicon-menu-down")
        PlaceholderHandler.set_placeholder_dropdown(el)
        cls._set_by_typeahead.add(parent_id)

    @classmethod
    def _reset_typeaheads(cls):
        """
        Reset all values set by typeahead back to default.
        """
        for el_id in cls._set_by_typeahead:
            window.destroy_typeahead_tag("#" + el_id)

        cls._set_by_typeahead = set()

    @classmethod
    def set_el(cls, el, value):
        """
        Set given `el` tag element to `value`.

        Automatically choose proper method to set the `value` based on the type
        of the `el`.

        Args:
            el (obj): Element reference to the input you want to convert to
                typeahead.
            value (list): List of dicts with two keys: ``source`` and ``val``.
        """
        if not el:
            return

        tag_name = el.elt.tagName.lower()
        if tag_name == "textarea":
            cls._set_textarea(el, value)
        elif tag_name == "input":
            if "typeahead" in el.class_name.lower():
                cls._set_typeahead(el, value)
            else:
                cls._set_input(el, value)
        elif tag_name == "select":
            pass  # TODO: implement selecting of the keywords
        else:  # TODO: Replace with exception
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )

    @staticmethod
    def get_el(el):
        tag_name = el.elt.tagName.lower()
        if tag_name == "textarea":
            return el.text
        elif tag_name == "input":
            return el.value
        elif tag_name == "select":
            pass  # TODO: implement selecting of the keywords
        else:  # TODO: Replace with exception
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )


class View(object):
    def __init__(self):
        # all kind of progress bars and error boxes
        self.log_view = LogView
        self.progress_bar = ProgressBar
        self.urlbox_error = UrlBoxError
        self.issnbox_error = ISSNBoxError
        self.conspect_handler = ConspectHandler
        self.user_kw_handler = UserKeywordHandler
        self.aleph_kw_handler = AlephKeywordHandler
        self.analysis_kw_handler = AanalysisKeywordHandler
        self.input_controller = InputController

        self._url_el = document["url"]
        self._issn_el = document["issn"]
        self._title_el = document["title"]
        self._creation_date_el = document["creation_date"]
        self._author_el = document["author"]
        self._place_el = document["place"]
        self._language_el = document["lang"]
        self._annotation_el = document["annotation"]
        self._periodicity_el = document["periode"]
        self._frequency_el = document["freq"]

    def reset(self):
        self.progress_bar.reset()
        self.progress_bar.show([0, 0])
        self.urlbox_error.reset()
        self.issnbox_error.reset()

        self.input_controller._reset_typeaheads()

    @property
    def url(self):
        return self.input_controller.get_el(self._url_el)

    @url.setter
    def url(self, val):
        self.input_controller.set_el(self._url_el, val)

    @property
    def issn(self):
        return self.input_controller.get_el(self._issn_el)

    @issn.setter
    def issn(self, val):
        self.input_controller.set_el(self._issn_el, val)

    @property
    def title(self):
        return self.input_controller.get_el(self._title_el)

    @title.setter
    def title(self, val):
        self.input_controller.set_el(self._title_el, val)

    @property
    def creation_date(self):
        return self.input_controller.get_el(self._creation_date_el)

    @creation_date.setter
    def creation_date(self, val):
        self.input_controller.set_el(self._creation_date_el, val)

    @property
    def author(self):
        return self.input_controller.get_el(self._author_el)

    @author.setter
    def author(self, val):
        self.input_controller.set_el(self._author_el, val)

    @property
    def place(self):
        return self.input_controller.get_el(self._place_el)

    @place.setter
    def place(self, val):
        self.input_controller.set_el(self._place_el, val)

    @property
    def keywords(self):
        dataset = [
            self.aleph_kw_handler.keywords,
            self.user_kw_handler.keywords,
            self.analysis_kw_handler.keywords,
        ]

        return sum(dataset, [])  # flattened dataset

    @property
    def language(self):
        return self.input_controller.get_el(self._language_el)

    @language.setter
    def language(self, val):
        self.input_controller.set_el(self._language_el, val)

    @property
    def annotation(self):
        value = self.input_controller.get_el(self._annotation_el)

        active_lines = [
            line.strip()
            for line in value.splitlines()
            if not line.strip().startswith("--")
        ]

        return "\n".join(active_lines)

    @annotation.setter
    def annotation(self, val):
        self.input_controller.set_el(self._annotation_el, val)

    @property
    def periodicity(self):
        return self.input_controller.get_el(self._periodicity_el)

    @periodicity.setter
    def periodicity(self, val):
        # custom handlers because of custom make_periode_typeahead_tag func
        parent_id = self._periodicity_el.parent.id
        if "typeahead" not in parent_id.lower():
            parent_id = self._periodicity_el.parent.parent.id

        if type(val) in [list, tuple] and len(val) > 1:
            window.make_periode_typeahead_tag("#" + parent_id, val)
            DropdownHandler.set_dropdown_glyph(
                self._periodicity_el.id,
                "glyphicon-menu-down"
            )
            return

        window.destroy_typeahead_tag("#" + parent_id)
        self.input_controller.set_el(self._periodicity_el, val)

    @property
    def frequency(self):
        return self.input_controller.get_el(self._frequency_el)

    @frequency.setter
    def frequency(self, val):
        self.input_controller.set_el(self._frequency_el, val)

    @property
    def conspect(self):
        return self.conspect_handler.get_dict()

    @conspect.setter
    def conspect(self, val):
        self.conspect_handler.set(val)

    def get_all_properties(self):
        def get_property_list(cls):
            return [
                prop_name
                for prop_name in dir(cls)
                if (isinstance(getattr(cls, prop_name), property) and
                    not prop_name.startswith("_"))
            ]

        properties = {
            prop_name: getattr(self, prop_name)
            for prop_name in get_property_list(self.__class__)
        }

        return properties

ViewController = View()
