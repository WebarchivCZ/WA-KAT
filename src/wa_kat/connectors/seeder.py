#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests

from .. import settings
from ..data_model import Model


# Variables ===================================================================
# Functions & classes =========================================================
def convert_to_mapping(seeder_struct):
    def pick_active(seeder_struct, what):
        items = seeder_struct.get(what)

        if not items:
            return None

        active_items = [item for item in items if items.get("active")]

        if not active_items:
            return items[0]

        return active_items[0]

    model = Model()

    active_seed = pick_active(seeder_struct, "seeds")
    publisher_contact = pick_active(
        seeder_struct.get("publisher", {}),
        "contacts"
    )

    if not active_seed:
        return None

    model.url = active_seed["url"]
    model.issn = seeder_struct.get("issn")
    model.title_tags = seeder_struct.get("name")
    model.publisher_tags = seeder_struct.get("publisher", {}).get("name")
    model.annotation_tags = seeder_struct.get("comment")  # annotation?

    conspect = None  # TODO: !

    if publisher_contact:
        model.place_tags = publisher_contact.get("address")

    # parse rules
    model.rules = {}
    model.rules["frequency"] = seeder_struct["frequency"]


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
