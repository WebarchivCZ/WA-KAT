#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import requests

from .. import settings
from ..data_model import Model


# Functions & classes =========================================================
def convert_to_mapping(seeder_struct):
    """
    Convert Seeder's structure to the internal structure used at frontend.

    Args:,
        seeder_struct (dict): Dictionary with Seeder data.

    Returns:
        obj: :class:`Model`.
    """
    def pick_active(seeder_struct, what):
        """
        From the list of dicts, choose only first of such, that contains
        ``"active": True`` item.

        If not found, just pick the first.

        Args:
            seeder_struct (dict): Dict with bunch of data.
            what (str): What key to use in `seeder_struct` to identify the
                list of dicts.

        Returns:
            dict: Active or first dict.
        """
        items = seeder_struct.get(what)

        if not items:
            return None

        active_items = [item for item in items if items.get("active")]

        if not active_items:
            return items[0]

        return active_items[0]

    # pick active seed and active publisher
    active_seed = pick_active(seeder_struct, "seeds")
    publisher_contact = pick_active(
        seeder_struct.get("publisher", {}),
        "contacts"
    )

    # seed contains `url`, which is used as primary key - if no seed is found,
    # it is meaningless to continue
    if not active_seed:
        return None

    # create the model and fill it with data
    model = Model()
    model.url = active_seed["url"]
    model.issn = seeder_struct.get("issn")
    model.title_tags = seeder_struct.get("name")
    model.publisher_tags = seeder_struct.get("publisher", {}).get("name")
    model.annotation_tags = seeder_struct.get("comment")  # annotation?

    conspect = None  # TODO: !

    if publisher_contact:
        model.place_tags = publisher_contact.get("address")

    # rules are stored in custom subdictionary
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
