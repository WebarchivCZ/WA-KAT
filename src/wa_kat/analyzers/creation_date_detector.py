#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Functions for parsing informations about date when the page / domain was
created.
"""
#
# Imports =====================================================================
import requests
import pythonwhois
from kwargs_obj import KwargsObj

from ..settings import WHOIS_URL


# Variables ===================================================================
class TimeResource(KwargsObj):
    """
    This class is backward compatible with :class:`.SourceString`, so it may
    be used to transport backend data to frontend.

    Attributes:
        url (str): URL of the additional informations.
        date (str): ISO 8601 date strings.
        val (str): Year as string.
        source (str): Information about origin of the source.
    """
    def __init__(self, **kwargs):
        self.url = None
        self.date = None

        # for backward compatibility with SourceString
        self.val = None
        self.source = None

        self._kwargs_to_attributes(kwargs)

    def to_dict(self):
        """
        Convert yourself to dictionary.
        """
        return {
            key: val
            for key, val in self.__dict__.iteritems()
        }

    def __str__(self):
        return self.val

    def __repr__(self):
        return "%s(%s)" % (self.source, self.val)


# Functions & classes =========================================================
def mementoweb_api_tags(url):
    """
    Parse list of :class:`TimeResource` objects based on the mementoweb.org.

    Args:
        url (str): Any url.

    Returns:
        list: :class:`TimeResource` objects.
    """
    memento_url = "http://labs.mementoweb.org/timemap/json/"

    r = requests.get(memento_url + url)

    if r.status_code != 200:
        return []

    data = r.json().get("mementos", {}).get("list", [])

    if not data:
        return []

    resources = (
        TimeResource(
            url=item.get("uri", ""),
            date=item.get("datetime", ""),
            val=item.get("datetime", "").split("-")[0],
            source="MementoWeb.org",
        )
        for item in data
    )

    # deduplicate the resources
    resource_dict = {
        res.val: res
        for res in resources
    }

    return sorted(resource_dict.values(), key=lambda x: x.val)


def get_whois_tags(domain):
    """
    Get :class:`TimeResource` objects with creation dates from Whois database.

    Args:
        domain (str): Domain without http://, relative paths and so on.

    Returns:
        list: :class:`TimeResource` objects.
    """
    data = pythonwhois.get_whois(domain)

    return [
        TimeResource(
            url=WHOIS_URL % domain.strip(),
            date=date.isoformat("T"),
            val=date.strftime("%Y"),
            source="Whois",
        )
        for date in data.get("creation_date", [])
    ]


def get_creation_date_tags(url, domain, as_dicts=False):
    """
    Put together all data sources in this module and return it's output.

    Args:
        url (str): URL of the web. With relative paths and so on.
        domain (str): Just the domain of the web.
        as_dicts (bool, default False): Convert output to dictionaries
            compatible with :class:`.SourceString`?

    Returns:
        list: Sorted list of :class:`TimeResource` objects or dicts.
    """
    creation_date_tags = [
        mementoweb_api_tags(url),
        get_whois_tags(domain),
    ]

    creation_date_tags = sorted(
        sum(creation_date_tags, []),
        key=lambda x: x.date
    )

    if not as_dicts:
        return creation_date_tags

    return [
        item._as_dict()
        for item in creation_date_tags
    ]
