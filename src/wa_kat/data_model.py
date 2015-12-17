#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import OrderedDict

from kwargs_obj import KwargsObj

import analyzers


# Functions & classes =========================================================
class Model(KwargsObj):
    def __init__(self, **kwargs):
        self.url = None
        self.title_tags = None
        self.creation_dates = None
        self.author_tags = None
        self.place_tags = None
        self.keyword_tags = None
        self.conspect = None
        self.lang_tags = None
        self.annotation_tags = None
        self.periodicity = None

        self._kwargs_to_attributes(kwargs)

    @classmethod
    def analyzers_mapping(cls):
        from zeo import ConspectDatabase

        return cls(
            title_tags=lambda self: analyzers.get_title_tags(self.index),
            place_tags=lambda self: analyzers.get_place_tags(
                self.index,
                self.domain
            ),
            lang_tags=lambda self: analyzers.get_lang_tags(self.index),
            keyword_tags=lambda self: analyzers.get_keyword_tags(self.index),
            author_tags=lambda self: analyzers.get_author_tags(self.index),
            annotation_tags=lambda self: analyzers.get_annotation_tags(
                self.index
            ),
            creation_dates=lambda self: analyzers.get_creation_date_tags(
                self.url,
                self.domain
            ),
            conspect=lambda self: ConspectDatabase().data,
        )

    def get_mapping(self):
        return OrderedDict(
            (key, val)
            for key, val in self.__dict__.iteritems()
            if val
        )
