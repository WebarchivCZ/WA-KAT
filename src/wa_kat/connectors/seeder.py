#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used as connector to Seeder - currator's application, which may
act as a source for some of the metadata.
"""
#
# Imports =====================================================================
import sys

import requests

from .. import settings
from ..data_model import Model
from ..analyzers.source_string import SourceString


# Functions & classes =========================================================
def _convert_to_wakat_format(seeder_struct):
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

        if not (isinstance(items, list) or isinstance(items, tuple)):
            items = [items]

        active_items = [item for item in items if item.get("active")]

        if not active_items:
            return items[0]

        return active_items[0]

    if not seeder_struct:
        return None

    # pick active seed and active publisher
    active_seed = pick_active(seeder_struct, "seeds")
    publisher_contact = pick_active(
        seeder_struct.get("publisher", {}),
        "contacts"
    )

    # seed contains `url`, which is used as primary key - if no seed is found,
    # it is meaningless to continue
    if not active_seed:
        active_seed = pick_active(seeder_struct, "seed")  # alt naming
        if not active_seed:
            return None

    # create the model and fill it with data
    model = Model()
    model.url = active_seed["url"]
    model.issn = seeder_struct.get("issn")
    model.title_tags = seeder_struct.get("name")
    model.publisher_tags = seeder_struct.get("publisher", {}).get("name")
    model.annotation_tags = seeder_struct.get("comment")  # annotation?

    # conspect = None  # TODO: !

    if publisher_contact:
        model.place_tags = publisher_contact.get("address")

    # rules are stored in custom subdictionary
    model.rules = {}
    model.rules["frequency"] = str(seeder_struct.get("frequency"))

    # add source info
    for key in model.keys():
        val = getattr(model, key)
        if val and "tags" in key:
            setattr(model, key, [{"val": val, "source": "Seeder"}])

    return model.get_mapping()


def _send_request(url_id, data=None, json=None, req_type=None):
    """
    Send request to Seeder's API.

    Args:
        url_id (str): ID used as identification in Seeder.
        data (obj, default None): Optional parameter for data.
        json (obj, default None): Optional parameter for JSON body.
        req_type (fn, default None): Request method used to send/download the
            data. If none, `requests.get` is used.

    Returns:
        dict: Data from Seeder.
    """
    url = settings.SEEDER_INFO_URL % url_id

    if not req_type:
        req_type = requests.get

    resp = req_type(
        url,
        data=data,
        json=json,
        timeout=settings.SEEDER_TIMEOUT,
        headers={
            "User-Agent": settings.USER_AGENT,
            "Authorization": settings.SEEDER_TOKEN,
        }
    )
    resp.raise_for_status()
    data = resp.json()

    return data


def get_remote_info(url_id):
    """
    Download data and convert them to dict used in frontend.

    Args:
        url_id (str): ID used as identification in Seeder.

    Returns:
        dict: Dict with data for frontend or None in case of error.
    """
    try:
        data = _send_request(url_id)
    except Exception as e:
        sys.stderr.write("Seeder GET error: ")  # TODO: better!
        sys.stderr.write(str(e.message))
        return None

    return _convert_to_wakat_format(data)


def _convert_to_seeder_format(dataset):
    """
    WA KAT dataset has different structure from Seeder. This is convertor
    which converts WA-KAT -> Seeder data format.

    Args:
        dataset (dict): WA-KAT dataset sent from frontend.

    Returns:
        dict: Dict with converted data.
    """
    data = {}
    seed = {}

    def add_if_set(d, key, val):
        if val:
            d[key] = val

    add_if_set(data, "name", dataset.get("title"))
    add_if_set(data, "issn", dataset.get("issn"))
    add_if_set(data, "annotation", dataset.get("annotation"))

    rules = dataset.get("rules", {})
    if rules:
        add_if_set(data, "frequency", rules.get("frequency"))

        # set seed info
        add_if_set(seed, "budget", rules.get("budget"))
        add_if_set(seed, "calendars", rules.get("calendars"))
        add_if_set(seed, "global_reject", rules.get("global_reject"))
        add_if_set(seed, "gentle_fetch", rules.get("gentle_fetch"))
        add_if_set(seed, "javascript", rules.get("javascript"))
        add_if_set(seed, "local_traps", rules.get("local_traps"))
        add_if_set(seed, "youtube", rules.get("youtube"))

        add_if_set(seed, "url", dataset.get("url"))

    if seed:
        data["seed"] = seed

    return data


def send_update(url_id, dataset):
    """
    Send request to Seeder's API with data changed by user.

    Args:
        url_id (str): ID used as identification in Seeder.
        dataset (dict): WA-KAT dataset sent from frontend.
    """
    data = _convert_to_seeder_format(dataset)

    if not data:
        return

    try:
        _send_request(url_id, json=data, req_type=requests.patch)
    except Exception as e:
        sys.stderr.write("Seeder PATCH error: ")  # TODO: better!
        sys.stderr.write(str(e.message))
        return None
