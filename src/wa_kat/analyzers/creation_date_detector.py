#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests
from kwargs_obj import KwargsObj


# Variables ===================================================================
class TimeResource(KwargsObj):
    def __init__(self, **kwargs):
        self.url = None
        self.date = None

        # for backward compatibility with SourceString
        self.val = None
        self.source = None

        self._kwargs_to_attributes(kwargs)

    def _as_dict(self):
        return {
            key: val
            for key, val in self.__dict__.iteritems()
        }

    def __str__(self):
        return self.val

    def __repr__(self):
        return "%s(%s)" % (self.source, self.val)


# Functions & classes =========================================================
def mementoweb_api(url):
    memento_url = "http://labs.mementoweb.org/timemap/json/"

    r = requests.get(memento_url + url)  # TODO: error handling

    data = r.json().get("mementos", {}).get("list", [])

    if not data:
        return []

    return [
        TimeResource(
            url=item.get("uri", ""),
            date=item.get("datetime", ""),
            val=item.get("datetime", "").split("-")[0],
            source="MementoWeb.org",
        )
        for item in data
    ]


def get_creation_date_tags(url, domain):
    return []


print mementoweb_api("http://kitakitsune.org")