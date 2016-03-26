#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This file is used as definition of data:

    - stored in database
    - sent from backend to frontend
    - transported from Aleph to frontend
"""
#
# Imports =====================================================================
from collections import namedtuple

from kwargs_obj import KwargsObj

import analyzers


# Functions & classes =========================================================
class FuncInfo(namedtuple("FuncInfo", ["func", "args_func"])):
    """
    Container for functions and it's arguments.

    Attributes:
        func (ref): Function reference.
        args_func (list): List of function arguments.
    """


def _compose_func(func, args_func=lambda req_info: [req_info.index]):
    """
    Compose function used to compose arguments to function.

    Arguments for the functions are composed from the :class:`.RequestInfo`
    object from the ZODB.
    """
    return FuncInfo(func=func, args_func=args_func)


class Model(KwargsObj):
    """
    This class is used as definition of all fields transported from backend
    to frontend (analysis, Aleph query), and also all fields stored in
    database.

    Any of the field may be set to ``None`` and in that case is ignore.
    """
    def __init__(self, **kwargs):
        self.url = None  #: URL of the resource.
        self.title_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.subtitle_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.creation_dates = None  #: List of dicts ``{source: .., val:..}``.
        self.author_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.publisher_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.place_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.keyword_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.conspect = None  #: Conspect code.
        self.lang_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.annotation_tags = None  #: List of dicts ``{source: .., val:..}``.
        self.periodicity = None  #: Periodicity string.
        self.source_info = None  #: 500a field from Aleph.
        self.original_xml = None  #: MARC XML record from Aleph.
        self.issn = None  #: ISSN, if defined.
        self.rules = None  #: Rules from the Seeder.
        self.additional_info = None  #: Additional fields from Aleph.

        self._kwargs_to_attributes(kwargs)

    @classmethod
    def analyzers_mapping(cls):
        """
        Return instance of itself where all used properties are set to
        :class:`FuncInfo`.

        This method is used by the database, which map all the properties
        defined here to itself, runs the functions as new processes and stores
        the result in itself. Because it knows how many properties are there,
        it may also track the progress, which is then transported to the
        frontend and displayed in form of progress bar.

        Returns:
            obj: :class:`Model` instance.
        """
        return cls(
            title_tags=_compose_func(analyzers.get_title_tags),
            place_tags=_compose_func(
                analyzers.get_place_tags,
                lambda req_info: (req_info.index, req_info.domain)
            ),
            lang_tags=_compose_func(analyzers.get_lang_tags),
            keyword_tags=_compose_func(analyzers.get_keyword_tags),
            # yep, authors of webpage are actually publishers
            publisher_tags=_compose_func(analyzers.get_author_tags),
            annotation_tags=_compose_func(analyzers.get_annotation_tags),
            creation_dates=_compose_func(
                analyzers.get_creation_date_tags,
                lambda req_info: (req_info.url, req_info.domain)
            ),
        )

    def keys(self):
        """
        Return list of properties.
        """
        return self.__dict__.keys()

    def get_mapping(self):  # TODO: rename to _as_dict
        """
        Convert the class to dict.

        Returns:
            dict: Copy of ``self.__dict__``.
        """
        return {
            key: val
            for key, val in self.__dict__.iteritems()
            if val
        }

    def __repr__(self):
        params = ", ".join(
            "%s=%s" % (key, repr(val))
            for key, val in self.__dict__.iteritems()
        )

        return "%s(%s)" % (self.__class__.__name__, params)
