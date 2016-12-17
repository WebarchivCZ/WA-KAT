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

from backports.functools_lru_cache import lru_cache

from ..logger import logger
from ..data_model import Model

from ..settings import ZEO_CACHE_TIME
from ..settings import ZEO_MAX_WAIT_TIME

from .worker import worker
from .downloader import download


# Functions ===================================================================
@lru_cache()
def worker_mapping():
    return Model().analyzers_mapping().get_mapping()


# Classes =====================================================================
class Progress(namedtuple("Progress", ["done", "base"])):
    """
    Progress bar representation.

    Attr:
        done (int): How much is done.
        base (int): How much is there.
    """


# ORM =========================================================================
class RequestInfo(object):
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.index = None

        self.creation_ts = time.time()
        self.downloaded_ts = None
        self.processing_started_ts = None
        self.processing_ended_ts = None

        for key in worker_mapping().keys():
            setattr(self, key, None)

    def _set_property(self, name, value):
        if name in worker_mapping().keys():
            setattr(self, name, value)
            return

        raise ValueError("Can't set `%s`!" % name)

    def _reset_set_properties(self):
        """
        Reset the progress counter back to zero.
        """
        for property_name in worker_mapping().keys():
            setattr(self, property_name, None)

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

    def _is_all_set(self):
        """
        Is all properties set?

        Returns:
            bool: True if they are set.
        """
        return self._get_all_set_properties() == set(worker_mapping().keys())

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

    def is_old(self):
        """
        Is the object cached for too long, so it should be redownloaded?

        See :attr:`.ZEO_MAX_WAIT_TIME` and :attr:`.ZEO_CACHE_TIME` for details.

        Returns:
            bool: True if it is.
        """
        if not self.processing_started_ts:
            return True

        if self.processing_ended_ts:
            return self.processing_ended_ts + ZEO_CACHE_TIME < time.time()

        # in case that processing started, but didn't ended in
        # ZEO_MAX_WAIT_TIME
        expected_end_ts = self.creation_ts + ZEO_MAX_WAIT_TIME
        if expected_end_ts < time.time():
            logger.error("Prosessing timeouted and properites were not set!")

        return expected_end_ts < time.time()

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
            "all_set": self._is_all_set(),
            "progress": self.progress(),
            "values": {
                property_name: getattr(self, property_name) or []
                for property_name in worker_mapping().keys()
            }
        }

    def paralel_processing(self):
        """
        Lauch paralel processes (see :func:`.worker`) to fill properties with
        data.

        Args:
        """
        self._reset_set_properties()

        self.index = download(self.url)
        self.downloaded_ts = time.time()
        self.processing_started_ts = time.time()

        # launch all workers as paralel processes
        for name, function_info in worker_mapping().iteritems():
            p = Process(
                target=worker,
                kwargs={
                    "url_key": self.url,
                    "property_name": name,
                    "function": function_info.func,
                    "function_arguments": function_info.args_func(self),
                }
            )
            p.start()
