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
from functools import total_ordering

import requests
from persistent import Persistent
from zeo_connector import transaction_manager
from backports.functools_lru_cache import lru_cache

from .. import analyzers
from worker import worker
from ..settings import ZEO_CACHE_TIME
from ..settings import ZEO_MAX_WAIT_TIME


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
def _get_req_mapping():
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
    ]

    # construct the OrderedDict - I want the order preserved
    return OrderedDict(
        (req.name, req)
        for req in REQ_MAPPING
    )


class Progress(namedtuple("Progress", ["done", "base"])):
    """
    Progress bar representation.

    Attr:
        done (int): How much is done.
        base (int): How much is there.
    """


@total_ordering
class RequestInfo(Persistent):
    """
    This object is used to hold informations about requests, which are
    processed at that moment. It stores all its properites in ZODB.

    The object is basically used as cache AND progress bar indicator of work.

    Attributes:
        url (str): URL to which this info object is related.
        domain (str): Domain of the URL.
        index (str): Content of the index page of URL.
        creation_ts (float): Timestamp of object creation.
        downloaded_ts (float): Timestamp showing where the :attr:`index` was
            downloaded.
        processing_started_ts (float): Timestamp showing when the processing of
            additional properties started.
        processing_ended_ts (float): Timestamp showing when the processing of
            additional properties stopped.

    Warning:
        There is more properties, one for all analyzator function from
        :mod:`.analyzers`.
    """
    def __init__(self, url):
        """
        Constructor.

        Args:
            url (str): URL to which this request is related.
        """
        self.url = url
        self.domain = urlparse(url).netloc
        self.index = None

        # time trackers
        self.creation_ts = time.time()
        self.downloaded_ts = None
        self.processing_started_ts = None
        self.processing_ended_ts = None

        for req in _get_req_mapping().values():
            setattr(self, req.name, None)

    def _download(self, url):
        """
        Download `url` and return it as utf-8 encoded text.

        Args:
            url (str): What should be downloaded?

        Returns:
            str: Content of the page.
        """
        resp = requests.get(url)  # TODO: custom headers

        return resp.text.encode("utf-8")  # TODO: what about binaries?

    @transaction_manager
    def paralel_processing(self, client_conf=None):
        """
        Lauch paralel processes (see :func:`.worker`) to fill properties with
        data.

        Args:
            client_conf (str, default None): Optional parameter used by tests
                to redirect the database connections to test's environment.
        """
        self.index = self._download(self.url)
        self.downloaded_ts = time.time()
        self.processing_started_ts = time.time()

        # launch all workers as paralel processes
        for pi in _get_req_mapping().values():
            p = Process(
                target=worker,
                kwargs={
                    "url_key": self.url,
                    "property_info": pi,
                    "filler_params": pi.filler_params(self),
                    "conf_path": client_conf,
                }
            )
            p.start()

    @transaction_manager
    def _get_all_set_properties(self):
        """
        Collect names of set properties.

        Returns:
            set: Set containing names of all properties, which are set to \
                 non-None value.
        """
        return set(
            property_name
            for property_name in _get_req_mapping().keys()
            if getattr(self, property_name) is not None
        )

    def progress(self):
        """
        Get progress.

        Returns:
            namedtuple: :class:`Progress`.
        """
        return Progress(
            done=len(self._get_all_set_properties()),
            base=len(_get_req_mapping()),
        )

    def is_all_set(self):
        """
        Is all properties set?

        Returns:
            bool: True if they are set.
        """
        return self._get_all_set_properties() == set(_get_req_mapping().keys())

    @transaction_manager
    def is_old(self):
        """
        Is the object cached for too long, so it should be redownloaded?

        See :attr:`.ZEO_MAX_WAIT_TIME` and :attr:`.ZEO_CACHE_TIME` for details.

        Returns:
            bool: True if it is.
        """
        if not self.processing_started_ts:
            return True

        # in case that processing started, but didn't ended in
        # ZEO_MAX_WAIT_TIME
        expected_end_ts = self.creation_ts + ZEO_MAX_WAIT_TIME
        not_ended = not (self.processing_ended_ts or self.is_all_set())
        if not_ended and expected_end_ts < time.time():
            return True

        return self.processing_ended_ts + ZEO_CACHE_TIME < time.time()

    @transaction_manager
    def to_dict(self):
        """
        This method is used in with connection to REST API. It basically
        converts all important properties to dictionary, which may be used by
        frontend.

        Returns:
            dict: ``{"all_set": bool, "progress": [int(done), int(how_many)], \
                  "values": {"property": [values], ..}}``
        """
        return {
            "all_set": self.is_all_set(),
            "progress": self.progress(),
            "values": {
                property_name: [
                    tag.to_dict()
                    for tag in getattr(self, property_name) or []
                ]
                for property_name in _get_req_mapping().keys()
            }
        }

    def __eq__(self, obj):
        if not isinstance(obj, RequestInfo):
            return False

        return self.url == obj.url

    def __lt__(self, obj):
        return float(self.creation_ts).__lt__(obj.creation_ts)

    def _p_resolveConflict(self, oldState, savedState, newState):
        """
        This method is used to resolve conflicts in ZODB, when two processes
        create two mismatched transactions. Which actually happens all the
        time.

        Standard ZODB stuff, just google it.
        """
        # for native properties ..
        native_properties = {
            "url",
            "domain",
            # "index",  # this may be big, so don't merge it
            "creation_ts",
            "downloaded_ts",
            "processing_started_ts",
            "processing_ended_ts",
        }

        # .. just pick the biggest of the native properties
        for np_name in native_properties:
            oldState[np_name] = max({savedState[np_name], newState[np_name]})

        # for `mapping` properties perform the merge
        for name in _get_req_mapping().keys():
            # don't update None states - this is important for .is_all_set()
            if oldState[name] is None and savedState[name] is None and \
               newState[name] is None:
                continue

            # merge
            pool = set()
            if oldState[name]:
                pool.update(oldState[name])
            if savedState[name]:
                pool.update(savedState[name])
            if newState[name]:
                pool.update(newState[name])

            oldState[name] = sorted(list(pool))

        return oldState
