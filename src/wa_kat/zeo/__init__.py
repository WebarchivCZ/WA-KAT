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

import transaction
from persistent import Persistent
from persistent.list import PersistentList
# from BTrees.OOBTree import OOSet  TODO: remove if not used

import requests

from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler

from .. import analyzers
from ..settings import PROJECT_KEY
from ..settings import ZEO_CLIENT_PATH


# Variables ===================================================================
class PropertyInfo(namedtuple("PropertyInfo", ["name",
                                               "attr_type",
                                               "filler_func",
                                               "filler_params"])):
    """
    TODO: docstrings
    """


def get_req_mapping():
    REQ_MAPPING = [
        PropertyInfo(
            name="title_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_title_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="place_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_place_tags,
            filler_params=lambda self: self.domain,
        ),
        PropertyInfo(
            name="lang_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_lang_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="keyword_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_keyword_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="author_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_author_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="annotation_tags",
            attr_type=PersistentList,
            filler_func=analyzers.get_annotation_tags,
            filler_params=lambda self: self.index,
        ),
        PropertyInfo(
            name="creation_dates",
            attr_type=PersistentList,
            filler_func=analyzers.get_creation_date_tags,
            filler_params=lambda self: (self.url, self.domain),
        ),
    ]

    return OrderedDict(
        (req.name, req)
        for req in REQ_MAPPING
    )


# Functions & classes =========================================================
class Request(Persistent):
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.index = None

        # time trackers
        self.creation_ts = time.time()
        self.downloaded_ts = None
        self.processing_started_ts = None
        self.processing_ended_ts = None

        self._mapping = get_req_mapping()
        self._mapping_set = set(self._mapping)
        self._values_set = set()
        self._all_set = False

        for req in self._mapping.values():
            setattr(self, req.name, req.attr_type)

    def _download(self, url):
        resp = requests.get(url)  # TODO: custom headers

        return resp.text.encode("utf-8")

    @transaction_manager
    def paralel_download(self):
        self.index = self._download(self.url)
        self.downloaded_ts = time.time()

        def worker(url, property_info, params):
            db = RequestDatabase()
            req = db.get_request(url)

            with transaction.manager:
                setattr(
                    req,
                    property_info.name,
                    property_info.filler_func(*params)
                )

        self.processing_started_ts = time.time()

        for pi in self._mapping:
            Process(
                target=worker,
                args=[self.url, pi, pi.filler_params(self)]
            )

    def __setattr__(self, name, value):
        """
        Track whether all values were set or not.
        """
        self.__dict__[name] = value
        self.__dict__["_values_set"].add(name)

        mapping_set = self._mapping_set
        if not self._all_set and self._values_set.issuperset(mapping_set):
            self.__dict__["processing_ended_ts"] = time.time()
            self.__dict__["_all_set"] = True

    def to_dict(self):
        pass


class RequestDatabase(DatabaseHandler):
    def __init__(self, conf_path=ZEO_CLIENT_PATH, project_key=PROJECT_KEY):
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        self.request_key = "requests"
        self.requests = self._get_key_or_create(self.request_key)

    @transaction_manager
    def get_request(self, url):
        req = self.requests.get(url, None)

        # return already stored requests
        if url:
            return req

        # if not found, create new
        req = Request(url=url)
        self.requests[url] = req

        return req
