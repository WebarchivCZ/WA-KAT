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

from ..settings import DB_CACHE_TIME
from ..settings import DB_MAX_WAIT_TIME

from .worker import worker
from .downloader import download


# Functions ===================================================================
@lru_cache()
def worker_mapping():
    """
    Return properties from :class:`Model`, which are transported from backend
    to frontend.

    Returns:
        dict: Dict {`property_name`: `func_info`} (func_info is for worker).
    """
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
    """
    This object is used to hold informations about requests, which are
    processed at that moment.

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
        :mod:`.analyzers` see :func:`worker_mapping` for details.
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

        self.creation_ts = time.time()
        self.downloaded_ts = None
        self.processing_started_ts = None
        self.processing_ended_ts = None

        for key in worker_mapping().keys():
            setattr(self, key, None)

    def _set_property(self, name, value):
        """
        Set property `name` to `value`, but only if it is part of the mapping
        returned from `worker_mapping` (ie - data transported to frontend).

        This method is used from the REST API DB, so it knows what to set and
        what not, to prevent users from setting internal values.

        Args:
            name (str): Name of the property to set.
            value (obj): Any python value.

        Raises:
            KeyError: If `name` can't be set.
        """
        if name in worker_mapping().keys():
            setattr(self, name, value)
            return

        raise KeyError("Can't set `%s`!" % name)

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

        See :attr:`.DB_MAX_WAIT_TIME` and :attr:`.DB_CACHE_TIME` for details.

        Returns:
            bool: True if it is.
        """
        if not self.processing_started_ts:
            return True

        if self.processing_ended_ts:
            return self.processing_ended_ts + DB_CACHE_TIME < time.time()

        # in case that processing started, but didn't ended in
        # DB_MAX_WAIT_TIME
        expected_end_ts = self.creation_ts + DB_MAX_WAIT_TIME
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
        Lauch paralel processes (see :func:`.worker`) to asynchrnously fill
        properties with data.
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
