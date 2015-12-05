#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
from urlparse import urlparse
from collections import namedtuple
from multiprocessing import Process
from functools import total_ordering

import requests
import transaction
from persistent import Persistent
from zeo_connector import transaction_manager

from ..settings import ZEO_CACHE_TIME
from ..settings import REQUEST_TIMEOUT
from ..settings import ZEO_MAX_WAIT_TIME
from ..worker_mapping import worker_mapping

from worker import worker


# Functions & classes =========================================================
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

        for req in worker_mapping().values():
            setattr(self, req.name, None)

    def _download(self, url):
        """
        Download `url` and return it as utf-8 encoded text.

        Args:
            url (str): What should be downloaded?

        Returns:
            str: Content of the page.
        """
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)  # TODO: custom headers

        return resp.text.encode("utf-8")  # TODO: what about binaries?

    def paralel_processing(self, client_conf=None):
        """
        Lauch paralel processes (see :func:`.worker`) to fill properties with
        data.

        Args:
            client_conf (str, default None): Optional parameter used by tests
                to redirect the database connections to test's environment.
        """
        self._reset_set_properties()

        with transaction.manager:
            self.index = self._download(self.url)
            self.downloaded_ts = time.time()
            self.processing_started_ts = time.time()

        # launch all workers as paralel processes
        for pi in worker_mapping().values():
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
    def _reset_set_properties(self):
        """
        Reset the progress counter back to zero.
        """
        for property_name in worker_mapping().keys():
            setattr(self, property_name, None)

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
            for property_name in worker_mapping().keys()
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
            base=len(worker_mapping()),
        )

    def is_all_set(self):
        """
        Is all properties set?

        Returns:
            bool: True if they are set.
        """
        return self._get_all_set_properties() == set(worker_mapping().keys())

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
                for property_name in worker_mapping().keys()
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
        for name in worker_mapping().keys():
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
