#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import socket
from urlparse import urlparse

import dhtmlparser
from ipwhois import IPWhois

from shared import parse_meta
from source_string import SourceString


# Functions & classes =========================================================
def _get_ip_address(domain):
    if "://" not in domain:
        domain = "http://" + domain

    hostname = urlparse(domain).netloc

    if not hostname:
        raise ValueError("Can't parse hostname!")

    return socket.gethostbyname(hostname)


def _get_html_geo_place_tags(index_page):
    """
    Return `languages` stored in dublin core ``<meta>`` tags.
    """
    return parse_meta(index_page, "geo.placename", "HTML")


def _get_whois_tags(ip_address):
    whois = IPWhois(ip_address).lookup()
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
        if "address" not in net:
            continue

        address = net["address"]

        # filter company name
        if "description" in net:
            address = address.replace(net["description"], "").strip()

        address_list.append(address)

    return [
        SourceString(val, source="Whois")
        for val in set(cities + address_list)
    ]


# def _get_geoip_tag(ip_address):
#     pass


def get_place_tags(index_page, domain):
    ip_address = _get_ip_address(domain)
    dom = dhtmlparser.parseString(index_page)

    place_tags = [
        _get_html_geo_place_tags(dom),
        _get_whois_tags(ip_address),
        # [_get_geo_place_tag(ip_address)],
    ]

    return sum(place_tags, [])  # return flattened list