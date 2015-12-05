#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple
from collections import OrderedDict

from backports.functools_lru_cache import lru_cache

import analyzers


# Functions & classes =========================================================
class PropertyInfo(namedtuple("PropertyInfo", ["name",
                                               "filler_func",
                                               "filler_params"])):
    """
    This class is used to join one function (:attr:`filler_func`) from
    :mod:`.analyzers` with its parameters (:attr:`filler_params`) and to say,
    where it should be stored (:attr:`name`).

    Example::

        PropertyInfo(
            name="title_tags",
            filler_func=analyzers.get_title_tags,
            filler_params=lambda self: self.index,
        )

    Attributes:
        name (str): Name of the property, where the data should be stored.
        filler_func (fn ref): Reference to function, which will be called.
        filler_params (lambda self:): Lambda function, which returns the
            parameters for :attr:`filler_func`. Function takes one parameter,
            which contains the reference to :class:`.PropertyInfo` object in
            which the result is stored.
    """


@lru_cache()
def worker_mapping():
    """
    This function serves as joiner for functions from :mod:`analyzers`, to map
    them to properties, which will be stored in :class:`.RequestInfo` database
    object.

    I've decided to do it this way, because it will allow paralel processing
    of the properties/functions and also all configuration is at one place,
    instead of multiple places in object properties / methods and so on.

    Returns:
        OrderedDict: with :class:`.PropertyInfo` objects.
    """
    from zeo import ConspectDatabase

    REQ_MAPPING = [
        PropertyInfo(
            name="title_tags",
            filler_func=analyzers.get_title_tags,
            filler_params=lambda self: [self.index],
        ),
        PropertyInfo(
            name="place_tags",
            filler_func=analyzers.get_place_tags,
            filler_params=lambda self: [self.index, self.domain],
        ),
        PropertyInfo(
            name="lang_tags",
            filler_func=analyzers.get_lang_tags,
            filler_params=lambda self: [self.index],
        ),
        PropertyInfo(
            name="keyword_tags",
            filler_func=analyzers.get_keyword_tags,
            filler_params=lambda self: [self.index],
        ),
        PropertyInfo(
            name="author_tags",
            filler_func=analyzers.get_author_tags,
            filler_params=lambda self: [self.index],
        ),
        PropertyInfo(
            name="annotation_tags",
            filler_func=analyzers.get_annotation_tags,
            filler_params=lambda self: [self.index],
        ),
        PropertyInfo(
            name="creation_dates",
            filler_func=analyzers.get_creation_date_tags,
            filler_params=lambda self: (self.url, self.domain),
        ),
        PropertyInfo(
            name="conspect",
            filler_func=lambda: ConspectDatabase().data,
            filler_params=lambda self: [],
        ),
    ]

    # construct the OrderedDict - I want the order preserved
    return OrderedDict(
        (req.name, req)
        for req in REQ_MAPPING
    )
