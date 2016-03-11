#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple

from kwargs_obj import KwargsObj

import analyzers


# Functions & classes =========================================================
class FuncInfo(namedtuple("FuncInfo", ["func", "args_func"])):
    pass


def _compose_func(func, args_func=lambda self: [self.index]):
    return FuncInfo(func=func, args_func=args_func)


class Model(KwargsObj):
    def __init__(self, **kwargs):
        self.url = None
        self.title_tags = None
        self.subtitle_tags = None
        self.creation_dates = None
        self.author_tags = None
        self.publisher_tags = None
        self.place_tags = None
        self.keyword_tags = None
        self.conspect = None
        self.lang_tags = None
        self.annotation_tags = None
        self.periodicity = None
        self.source_info = None
        self.original_xml = None
        self.issn = None
        self.rules = None

        self._kwargs_to_attributes(kwargs)

    @classmethod
    def analyzers_mapping(cls):
        return cls(
            title_tags=_compose_func(analyzers.get_title_tags),
            place_tags=_compose_func(
                analyzers.get_place_tags,
                lambda x: (x.index, x.domain)
            ),
            lang_tags=_compose_func(analyzers.get_lang_tags),
            keyword_tags=_compose_func(analyzers.get_keyword_tags),
            # authors of webpage are actually publishers
            publisher_tags=_compose_func(analyzers.get_author_tags),
            annotation_tags=_compose_func(analyzers.get_annotation_tags),
            creation_dates=_compose_func(
                analyzers.get_creation_date_tags,
                lambda x: (x.url, x.domain)
            ),
        )

    def get_mapping(self):
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
