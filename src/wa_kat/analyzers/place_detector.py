#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Parse informations about city where the web is located.
"""
#
# Imports =====================================================================
import socket
from urlparse import urlparse

import dhtmlparser
from ipwhois import IPWhois

from shared import parse_meta
from source_string import SourceString


# Functions & classes =========================================================
def get_ip_address(domain):
    """
    Get IP address for given `domain`. Try to do smart parsing.

    Args:
        domain (str): Domain or URL.

    Returns:
        str: IP address.

    Raises:
        ValueError: If can't parse the domain.
    """
    if "://" not in domain:
        domain = "http://" + domain

    hostname = urlparse(domain).netloc

    if not hostname:
        raise ValueError("Can't parse hostname!")

    return socket.gethostbyname(hostname)


def get_html_geo_place_tags(index_page):
    """
    Get `languages` stored in dublin core ``<meta>`` tags.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    return parse_meta(index_page, "geo.placename", "HTML")


def get_whois_tags(ip_address):
    """
    Get list of tags with `address` for given `ip_address`.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    whois = IPWhois(ip_address).lookup_whois()
    nets = whois.get("nets", None)

    if not nets:
        return []

    # parse cities
    cities = [
        net["city"]
        for net in nets
        if net.get("city", None)
    ]

    # parse address tags
    address_list = []
    for net in nets:
        address = net.get("address", None)
        if not address:
            continue

        # filter company name
        if "description" in net and net["description"]:
            address = address.replace(net["description"], "").strip()

        if "\n" in address:
            address = ", ".join(address.splitlines())

        address_list.append(address)

    return [
        SourceString(val, source="Whois")
        for val in set(cities + address_list)
    ]


# def _get_geoip_tag(ip_address):  # TODO: implement geoip
#     pass


def get_place_tags(index_page, domain):  #: TODO geoip to docstring
    """
    Return list of `place` tags parsed from `meta` and `whois`.

    Args:
        index_page (str): HTML content of the page you wisht to analyze.
        domain (str): Domain of the web, without ``http://`` or other parts.

    Returns:
        list: List of :class:`.SourceString` objects.
    """
    ip_address = get_ip_address(domain)
    dom = dhtmlparser.parseString(index_page)

    place_tags = [
        get_html_geo_place_tags(dom),
        get_whois_tags(ip_address),
        # [_get_geo_place_tag(ip_address)],  # TODO: implement geoip
    ]

    return sum(place_tags, [])  # return flattened list
