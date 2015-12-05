#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import json
import os.path

import requests
import transaction
from persistent import Persistent
from zeo_connector.examples import DatabaseHandler

from ..settings import PROJECT_KEY
from ..settings import ZEO_CLIENT_PATH
from ..settings import CONSPECT_API_URL
from ..settings import CONSPECT_UPDATE_INTERVAL


# Variables ===================================================================
# Functions & classes =========================================================
def conspect_to_dict(original):
    def _process_subcategories(sub_category):
        return {
            cat["name"]: cat["subcategory_id"]
            for cat in sub_category
        }

    return {
        el["name"]: _process_subcategories(el["sub_categories"])
        for el in original
    }


class ConspectInfo(Persistent):
    def __init__(self):
        self.data = {}
        self.updated_ts = 0

    def is_set(self):
        return self.updated_ts != 0

    def _fallback_load(self):
        """
        Load static data only in case, that they weren't loaded before from
        the seeder.
        """
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, "../templates/conspect.json")

        with open(path) as f:
            self.data = json.loads(f.read())

    def update(self):
        try:
            resp = requests.get(CONSPECT_API_URL, timeout=3)
        except requests.exceptions.Timeout:
            # fallback in case that net doesn't work
            if not self.is_set:
                self._fallback_load()

            return

        with transaction.manager:
            self.data = resp.json()
            self.updated_ts = time.time()

    def timed_update(self):
        with transaction.manager:
            updated_ts = self.updated_ts

        if updated_ts + CONSPECT_UPDATE_INTERVAL < time.time():
            self.update()


class ConspectDatabase(DatabaseHandler):
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

        self._conspect_key = "conspect"
        self.conspect = self._get_key_or_create(
            key=self._conspect_key,
            obj_type=ConspectInfo,
        )

        if not self.conspect.is_set():
            self.conspect.update()

    @property
    def updated_ts(self):
        with transaction.manager:
            return self.conspect.updated_ts

    @updated_ts.setter
    def updated_ts(self, val):
        with transaction.manager:
            self.conspect.updated_ts = val

    @property
    def data(self):
        self.conspect.timed_update()

        with transaction.manager:
            data = self.conspect.data

        return conspect_to_dict(data)

    @data.setter
    def data(self, val):
        with transaction.manager:
            self.conspect.data = val
