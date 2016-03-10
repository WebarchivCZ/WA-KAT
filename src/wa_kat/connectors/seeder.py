#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json

import requests

from .. import settings
from ..data_model import Model


# Variables ===================================================================
# Functions & classes =========================================================
def convert_to_mapping(seeder_struct):
    model = Model()

    # prepsat všechno na .get()
    url = seeder_struct["seeds"][0]["url"] # TODO: pick fist active: true
    title_tags = seeder_struct["name"]
    creation_dates = None
    author_tags = None
    publisher_tags = None
    place_tags = None
    keyword_tags = None
    conspect = None
    lang_tags = None
    annotation_tags = seeder_struct["comment"]
    periodicity = None
    source_info = None
    original_xml = None
    issn = seeder_struct["issn"]


def get_remote_info(url_id):  # TODO: Add timeout, print error in case of exception
    url = settings.SEEDER_INFO_URL % url_id
    resp = requests.get(url, headers={
        "User-Agent": settings.USER_AGENT,
        "Authorization": settings.SEEDER_TOKEN,
    })
    resp.raise_for_status()
    data = resp.json()

    print data

    return data
