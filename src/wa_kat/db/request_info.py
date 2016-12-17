#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import time
import os.path
from urlparse import urlparse
from collections import namedtuple
from multiprocessing import Process

from pony import orm
from backports.functools_lru_cache import lru_cache

from ..logger import logger
from ..data_model import Model

from ..settings import ZEO_CACHE_TIME
from ..settings import ZEO_MAX_WAIT_TIME

from .worker import worker
from .downloader import download


# Variables ===================================================================
DB = orm.Database()
# DB.bind('sqlite', ':memory:')

if os.path.exists("/tmp/wa-kat_database.sqlite"):
    os.remove("/tmp/wa-kat_database.sqlite")
DB.bind('sqlite', '/tmp/wa-kat_database.sqlite', create_db=True)


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
class RequestInfo(DB.Entity):
    url = orm.PrimaryKey(str)
    domain = orm.Required(str)
    index = orm.Optional(str)

    creation_ts = orm.Optional(float)
    downloaded_ts = orm.Optional(float)
    processing_started_ts = orm.Optional(float)
    processing_ended_ts = orm.Optional(float)

    title_tags = orm.Optional(orm.Json)
    place_tags = orm.Optional(orm.Json)
    lang_tags = orm.Optional(orm.Json)
    keyword_tags = orm.Optional(orm.Json)
    publisher_tags = orm.Optional(orm.Json)
    annotation_tags = orm.Optional(orm.Json)
    creation_dates = orm.Optional(orm.Json)

    def __init__(self, url, domain=None):
        if not domain:
            domain = urlparse(url).netloc

        super(self.__class__, self).__init__(url=url, domain=domain)

        self.creation_ts = time.time()
        for key in worker_mapping().keys():
            setattr(self, key, None)

    @classmethod
    def get_by_url(cls, url, for_update=False):
        if for_update:
            return cls.get_for_update(url=url)

        return cls.get(url=url)

    @classmethod
    def get_cached_or_new(cls, url, new=False, for_update=False):
        old_req = cls.get_by_url(url, for_update=for_update)

        if old_req and not new:
            print "cached"  # TODO: remove
            return old_req

        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("Invalid URL `%s`!" % url)

        if old_req:
            old_req.delete()

        req = cls(url=url)
        orm.commit()

        print "new"  # TODO: remove
        return req

    def _reset_set_properties(self):
        """
        Reset the progress counter back to zero.
        """
        obj = self.get_by_url(self.url, for_update=True)
        for property_name in worker_mapping().keys():
            setattr(obj, property_name, None)

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
        def to_dict_list(seq):
            return [
                tag.to_dict()
                for tag in seq
            ]

        def process_property(val):
            if isinstance(val, dict):
                return val

            return to_dict_list(val)

        obj = self.get_by_url(self.url)
        return {
            "all_set": obj._is_all_set(),
            "progress": obj.progress(),
            "values": {
                property_name: process_property(
                    getattr(obj, property_name) or []
                )
                for property_name in worker_mapping().keys()
            }
        }

    @orm.db_session
    def paralel_processing(self):
        """
        Lauch paralel processes (see :func:`.worker`) to fill properties with
        data.

        Args:
        """
        obj = self.get_by_url(self.url, for_update=True)
        obj._reset_set_properties()

        obj.index = download(obj.url)
        obj.downloaded_ts = time.time()
        obj.processing_started_ts = time.time()

        # launch all workers as paralel processes
        for name, function_info in worker_mapping().iteritems():
            print "Launching %s, %s" % (name, function_info)
            p = Process(
                target=worker,
                kwargs={
                    "url_key": obj.url,
                    "property_name": name,
                    "function": function_info.func,
                    "function_arguments": function_info.args_func(obj),
                }
            )
            p.start()


DB.generate_mapping(create_tables=True)


# if __name__ == '__main__':
import os
if os.getenv("XE"):
    with orm.db_session:
        req = RequestInfo.get_cached_or_new("http://kitakitsune.org")
        req = RequestInfo.get_cached_or_new("http://kitakitsune.org")
        req.paralel_processing()

    while True:
        try:
            obj = RequestInfo.get_by_url("http://kitakitsune.org", for_update=True)
            # print obj.to_dict()
            orm.show(obj)
        except KeyboardInterrupt:
            break

        time.sleep(1)