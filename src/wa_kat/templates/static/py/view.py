#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import ajax

from browser import alert  # TODO: Remove
from browser import window
from browser import document

from components import ProgressBar
from components import UrlBoxError
from components import ISSNBoxError
from components import ConspectHandler
from components import DropdownHandler
from components import PlaceholderHandler
from components import KeywordListHandler


# Functions & classes =========================================================
class View(object):
    def __init__(self):
        # this is used to track what kind of elements were added by typeahead
        self._set_by_typeahead = set()

        # all kind of progress bars and error boxes
        self.progress_bar = ProgressBar
        self.urlbox_error = UrlBoxError
        self.issnbox_error = ISSNBoxError
        self.conspect_handler = ConspectHandler
        self.kw_list_handler = KeywordListHandler

    @property
    def _url_el(self):
        return document["url"]

    @property
    def _issn_el(self):
        return document["issn"]

    @property
    def _title_el(self):
        return document["title"]

    @property
    def _creation_date_el(self):
        return document["creation_date"]

    @property
    def _author_el(self):
        return document["author"]

    @property
    def _place_el(self):
        return document["place"]

    @property
    def _keywords_el(self):
        return document["keywords"]

    @property
    def _language_el(self):
        return document["lang"]

    @property
    def _annotation_el(self):
        return document["annotation"]

    @property
    def _periodicity_el(self):
        return document["periode"]

    @property
    def _frequency_el(self):
        return document["freq"]

    def _set_input(self, el, value):
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

    def _set_textarea(self, el, value):
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

    def _set_typeahead(self, el, value):
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

        # TODO: preserve old values
        if parent_id in self._set_by_typeahead:
            window.destroy_typyahead_tag("#" + parent_id)

        # if there are multiple elements, put them to the typeahead and show
        # dropdown glyph
        window.make_typeahead_tag("#" + parent_id, value)
        DropdownHandler.set_dropdown_glyph(el.id, "glyphicon-menu-down")
        PlaceholderHandler.set_placeholder_dropdown(el)
        self._set_by_typeahead.add(parent_id)

    def _reset_typeaheads(self):
        """
        Reset all values set by typeahead back to default.
        """
        for el_id in self._set_by_typeahead:
            window.destroy_typyahead_tag("#" + el_id)

        self._set_by_typeahead = set()

    def _set_el(self, el, value):
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
            self._set_textarea(el, value)
        elif tag_name == "input":
            if "typeahead" in el.class_name.lower():
                self._set_typeahead(el, value)
            else:
                self._set_input(el, value)
        elif tag_name == "select":
            pass  # TODO: implement selecting of the keywords
        else:  # TODO: Replace with exception
            alert(
                "Setter for %s (%s) not implemented!" % (tag_name, el.id)
            )

    def _get_el(self, el):
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

    def reset(self):
        self.progress_bar.reset()
        self.progress_bar.show([0, 0])
        self.urlbox_error.reset()
        self.issnbox_error.reset()

        self._reset_typeaheads()

    @property
    def url(self):
        return self._get_el(self._url_el)

    @url.setter
    def url(self, val):
        self._set_el(self._url_el, val)

    @property
    def issn(self):
        return self._get_el(self._issn_el)

    @issn.setter
    def issn(self, val):
        self._set_el(self._issn_el, val)

    @property
    def title(self):
        return self._get_el(self._title_el)

    @title.setter
    def title(self, val):
        self._set_el(self._title_el, val)

    @property
    def creation_date(self):
        return self._get_el(self._creation_date_el)

    @creation_date.setter
    def creation_date(self, val):
        self._set_el(self._creation_date_el, val)

    @property
    def author(self):
        return self._get_el(self._author_el)

    @author.setter
    def author(self, val):
        self._set_el(self._author_el, val)

    @property
    def place(self):
        return self._get_el(self._place_el)

    @place.setter
    def place(self, val):
        self._set_el(self._place_el, val)

    @property
    def keywords(self):
        return self.kw_list_handler.keywords

    @keywords.setter
    def keywords(self, val):
        self.kw_list_handler.keywords = []

        if type(val) in [list, tuple]:
            for keyword in val:
                if isinstance(keyword, dict):
                    keyword = keyword["val"]

                self.kw_list_handler.add_keyword(keyword)
        elif isinstance(val, dict):
            self.kw_list_handler.add_keyword(val["val"])
        else:
            self.kw_list_handler.add_keyword(val)

    @property
    def language(self):
        return self._get_el(self._language_el)

    @language.setter
    def language(self, val):
        self._set_el(self._language_el, val)

    @property
    def annotation(self):
        value = self._get_el(self._annotation_el)

        active_lines = [
            line.strip()
            for line in value.splitlines()
            if not line.strip().startswith("--")
        ]

        return "\n".join(active_lines)

    @annotation.setter
    def annotation(self, val):
        self._set_el(self._annotation_el, val)

    @property
    def periodicity(self):
        return self._get_el(self._periodicity_el)

    @periodicity.setter
    def periodicity(self, val):
        self._set_el(self._periodicity_el, val)

    @property
    def frequency(self):
        return self._get_el(self._periodicity_el)

    @periodicity.setter
    def periodicity(self, val):
        self._set_el(self._periodicity_el, val)

    @property
    def conspect(self):
        return self.conspect_handler.get()

    @conspect.setter
    def conspect(self, val):
        self.conspect_handler.set(val)

ViewController = View()
