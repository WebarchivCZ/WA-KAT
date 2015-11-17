#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from urlparse import urlparse
from collections import namedtuple
from collections import OrderedDict
from multiprocessing import Process

import requests
from persistent import Persistent
from zeo_connector import transaction_manager

from .. import analyzers
from worker import worker


# Functions & classes =========================================================
def _get_req_mapping():
    REQ_MAPPING = [
        PropertyInfo(
            name="title_tags",
            filler_func=analyzers.get_title_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="place_tags",
            filler_func=analyzers.get_place_tags,
            filler_params=lambda self: self.domain,
        ),
        PropertyInfo(
            name="lang_tags",
            filler_func=analyzers.get_lang_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="keyword_tags",
            filler_func=analyzers.get_keyword_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="author_tags",
            filler_func=analyzers.get_author_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="annotation_tags",
            filler_func=analyzers.get_annotation_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="creation_dates",
            filler_func=analyzers.get_creation_date_tags,
            filler_params=lambda self: (self.url, self.domain),
        ),
    ]

    return OrderedDict(
        (req.name, req)
        for req in REQ_MAPPING
    )


class PropertyInfo(namedtuple("PropertyInfo", ["name",
                                               "filler_func",
                                               "filler_params"])):
    """
    TODO: docstrings
    """


class RequestInfo(Persistent):
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.index = None

        # time trackers
        self.creation_ts = time.time()
        self.downloaded_ts = None
        self.processing_started_ts = None
        self.processing_ended_ts = None

        self._mapping = _get_req_mapping()

        for req in self._mapping.values():
            setattr(self, req.name, None)

    def _download(self, url):
        resp = requests.get(url)  # TODO: custom headers

        return resp.text.encode("utf-8")

    @transaction_manager
    def paralel_download(self):
        self.index = self._download(self.url)
        self.downloaded_ts = time.time()
        self.processing_started_ts = time.time()

        # launch all workers as paralel processes
        for pi in self._mapping.values():
            p = Process(
                target=worker,
                args=[self.url, pi, pi.filler_params(self)]
            )
            p.start()

    def is_all_set(self):
        mapping_set = set(self._mapping.keys())
        set_properties = set(
            property_name
            for property_name in mapping_set
            if getattr(self, property_name) is not None
        )

        return set_properties == mapping_set

    def to_dict(self):
        pass
