#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import transaction
from zeo_connector import transaction_manager
from zeo_connector.examples import DatabaseHandler

from ..settings import PROJECT_KEY
from ..settings import ZEO_CLIENT_PATH

from request_info import RequestInfo


# Variables ===================================================================
DAY = 60 * 60 * 24  #: Amount of seconds in one day.
YEAR = DAY * 356  #: Amount of seconds in one year.


# Functions & classes =========================================================
class RequestDatabase(DatabaseHandler):
    """
    Small database handler, which lets keeps track of currently running
    analysis. It also caches the requests, so it doesn't use that much
    resources.

    Attributes:
        request_key (str): Key which is used to access the ZODB.
        requests (OOTreeSet): Tree dictionary-like object under which the
            values are stored.
    """
    def __init__(self, conf_path=ZEO_CLIENT_PATH, project_key=PROJECT_KEY):
        """
        Constructor.

        Args:
            conf_path (str): Path to the ZEO client configuration file. Default
                :attr:`.ZEO_CLIENT_PATH`.
            project_key (str): Key which is used for whole DB. Default
                :attr:`.PROJECT_KEY`.
        """
        super(self.__class__, self).__init__(
            conf_path=conf_path,
            project_key=project_key
        )

        self.request_key = "requests"
        self.requests = self._get_key_or_create(self.request_key)

    def get_request(self, url, new=False):
        """
        For given `url` register new :class:`RequestInfo` object or return
        cached, if there is such.

        Args:
            url (str): Key for database under which the :class:`.RequestInfo`
                is stored.

        Returns:
            obj: Proper :class:`.RequestInfo` object.
        """
        with transaction.manager:
            old_req = self.requests.get(url, None)

        # return cached requests
        if old_req and not new:
            return old_req

        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("Invalid URL `%s`!" % url)

        # if not found, create new
        req = RequestInfo(url=url)

        with transaction.manager:
            if old_req:
                del self.requests[url]
                self.zeo.pack()

            self.requests[url] = req

        return req

    @transaction_manager
    def garbage_collection(self, time_limit=YEAR/2.0):
        """
        Collect and remove all :class:`.RequestInfo` objects older than
        `time_limit` (in seconds).

        Args:
            time_limit (float, default YEAR / 2): Collect objects older than
                this limit.
        """
        expired_ri_keys = [
            key
            for key, ri in self.requests.iteritems()
            if ri.creation_ts + time_limit <= time.time()
        ]

        for key in expired_ri_keys:
            del self.requests[key]

        self.zeo.pack()
