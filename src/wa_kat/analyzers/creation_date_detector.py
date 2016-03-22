#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests
import pythonwhois
from kwargs_obj import KwargsObj

from ..settings import WHOIS_URL


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
def _mementoweb_api_tags(url):
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


def _get_whois_tags(domain):
    data = pythonwhois.get_whois("kitakitsune.org")

    return [
        TimeResource(
            url=WHOIS_URL % domain.strip(),
            date=date.isoformat("T"),
            val=date.strftime("%Y"),
            source="Whois",
        )
        for date in data.get("creation_date", [])
    ]


def get_creation_date_tags(url, domain, as_dicts=True):
    return []


# print _mementoweb_api_tags("http://kitakitsune.org")[0].date
print _get_whois_tags("http://kitakitsune.org")
# print _get_whois_tags("188.213.170.140")
