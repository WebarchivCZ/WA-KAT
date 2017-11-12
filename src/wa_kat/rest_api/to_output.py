#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This part of the REST API joins the frontend dataset created by user with
convertors and connectors to various other parts of the WA-KAT backend, which
are used to fill missing data, and emit required output data.
"""
#
# Imports =====================================================================
import re
import json
import time
from os.path import join

from bottle import post
from bottle import SimpleTemplate
from bottle_rest import form_to_params

from marcxml_parser.tools.resorted import resorted

from ..settings import API_PATH

from ..convertors import to_dc
from ..convertors import mrc_to_marc
from ..convertors import item_to_mrc

from ..connectors.seeder import send_update

from shared import read_template

from keywords import keyword_to_info


# Functions & classes =========================================================
def compile_keywords(keywords):
    """
    Translate `keywords` to full keyword records as they are used in Aleph.

    Returns tuple with three lists, each of which is later used in different
    part of the MRC/MARC record.

    Args:
        keywords (list): List of keyword strings.

    Returns:
        tuple: (mdt_list, cz_keyword_list, en_keyword_list)
    """
    mdt = []
    cz_keywords = []
    en_keywords = []
    for keyword in keywords:
        keyword = keyword_to_info(keyword.encode("utf-8"))

        if not keyword:
            continue

        cz_keywords.append({
            "uid": keyword["uid"],
            "zahlavi": keyword["zahlavi"],
            "zdroj": "czenas",
        })

        if keyword.get("mdt"):
            mdt.append({
                "mdt": keyword["mdt"],
                "mrf": keyword["mrf"],
            })

        angl_ekvivalent = keyword.get("angl_ekvivalent")
        if angl_ekvivalent:
            en_keywords.append({
                "zahlavi": angl_ekvivalent,
                "zdroj": keyword.get("zdroj_angl_ekvivalentu") or "eczenas",
            })

    return mdt, cz_keywords, en_keywords


def render_mrc(data):
    """
    Render MRC template.

    Args:
        data (dict): Dictionary with data from the WA-KAT frontend.

    Returns:
        str: MRC template filled with `data`.
    """
    template_body = read_template("sablona_katalogizace_eperiodika.mrc")

    return SimpleTemplate(template_body).render(**data)


def url_to_fn(url):
    """
    Convert `url` to filename used to download the datasets.

    ``http://kitakitsune.org/xe`` -> ``kitakitsune.org_xe``.

    Args:
        url (str): URL of the resource.

    Returns:
        str: Normalized URL.
    """
    url = url.replace("http://", "").replace("https://", "")
    url = url.split("?")[0]

    return url.replace("%", "_").replace("/", "_")


def parse_date_range(date, alt_end_date=None):
    """
    Parse input `date` string in free-text format for four-digit long groups.

    Args:
        date (str): Input containing years.

    Returns:
        tuple: ``(from, to)`` as four-digit strings.
    """
    NOT_ENDED = "9999"
    all_years = re.findall(r"\d{4}", date)

    if alt_end_date:
        NOT_ENDED = alt_end_date

    if not all_years:
        return "****", NOT_ENDED

    elif len(all_years) == 1:
        return all_years[0], NOT_ENDED

    return all_years[0], all_years[1]


def serialize_author(author_data):
    """
    Author is passed as dictionary with parsed and raw data. This function adds
    *experimental support* for transport of all author fields based on RAW
    data, instead of parsed fields.

    If this proves as wrong, the code will be switched to use of parsed data
    again.

    Example of the input `author_data`::

       "author":{
          "name":"Grada Publishing",
          "code":"kn20080316009",
          "linked_forms":[
             "Grada Publishing a.s.",
             "Grada (nakladatelství)",
             "Nakladatelství Grada"
          ],
          "is_corporation":true,
          "record":{
             "7":[
                "kn20080316009"
             ],
             "i1":"2",
             "i2":" ",
             "a":[
                "Grada Publishing"
             ]
          },
          "alt_name":"Grada Publishing [organizace] (Grada Publishing a.s.,
                      Grada (nakladatelství), Nakladatelství Grada)"
        }

    This is transformed into::

        1102  L $$aGrada Publishing$$b $$7kn20080316009

    Fields used in the output are taken from the ``is_corporation``,
    ``record`` fields (``i1``, ``i2``, ``7`` and ``a``).

    Returns:
        str: String containing the line which will be included to the MRC.
    """
    record = author_data["record"]
    i1 = record["i1"]
    i2 = record["i2"]

    # make sure that all required fields will be created
    if "a" not in record:
        record["a"] = " "

    if author_data["is_corporation"]:
        code = "110"
        if "b" not in record:
            record["b"] = " "
    else:
        code = "100"
        if "d" not in record:
            record["d"] = " "
        if "4" not in record:
            record["4"] = " "

    out = "%s%s%s L " % (code, i1, i2)
    for key in resorted(key for key in record if len(key) == 1):
        for item in record[key]:
            out += "$$%s%s" % (key, item)

    return out


def get_008_lang_code(lang_code, default_lang="cze"):
    """
    008 lang code is always 3 characters long. Look at `language` info from the
    user's dataset and use it, if it is exactly 3 chars long.
    """
    if not lang_code:
        return default_lang

    if len(lang_code) != 3:
        return default_lang

    return lang_code


def _to_date_in_588(date_str):
    """
    Convert date in the format ala 03.02.2017 to 3.2.2017.

    Viz #100 for details.
    """
    try:
        date_tokens = (int(x) for x in date_str.split("."))
    except ValueError:
        return date_str

    return ".".join(str(x) for x in date_tokens)



# REST API ====================================================================
@post(join(API_PATH, "to_output"))
@form_to_params
def to_output(data):
    """
    Convert WA-KAT frontend dataset to three output datasets - `MRC`, `MARC`
    and `Dublin core`.

    Conversion is implemented as filling ofthe MRC template, which is then
    converted to MARC record. Dublin core is converted standalone from the
    input dataset.
    """
    data = json.loads(data)

    # postprocessing
    if "keywords" in data:
        mdt, cz_keywords, en_keywords = compile_keywords(data["keywords"])
        del data["keywords"]

        data["mdt"] = mdt
        data["cz_keywords"] = cz_keywords
        data["en_keywords"] = en_keywords

    data["annotation"] = data["annotation"].replace("\n", " ")
    data["time"] = time  # for date generation

    # convert additional info values to MRC
    ai_key = "additional_info"
    if data.get(ai_key) is None:
        data[ai_key] = {}

    # parse regularity - see https://github.com/WebArchivCZ/WA-KAT/issues/66
    # for details
    fld_008 = data[ai_key].get("008")
    data["regularity"] = fld_008[18] if fld_008 and len(fld_008) > 18 else "-"

    # put lang code to 008
    data["lang_code_008"] = get_008_lang_code(data.get("language"))

    # special format of date - viz #100
    data["date_of_generation"] = _to_date_in_588(time.strftime("%d.%m.%Y"))

    data[ai_key] = {
        key: "\n".join(item_to_mrc(key, val))
        for key, val in data[ai_key].iteritems()
        if val
    }

    alt_end_date = data[ai_key].get("alt_end_date", None)

    # handle date range in the 008
    from_year, to_year = parse_date_range(data["creation_date"], alt_end_date)
    data["from_year"] = from_year
    data["to_year"] = to_year

    # serialize author
    if data["author"]:
        data["serialized_author"] = serialize_author(data["author"])

    # send data to seeder
    if data.get("url_id"):
        send_update(data["url_id"], data)

    # convert to MRC format
    mrc = render_mrc(data).encode("utf-8")

    # create all output formats
    out = {
        "fn": url_to_fn(data["url"]),
        "mrc": mrc,
        "oai": mrc_to_marc(mrc),
        "dc": to_dc(data),
    }

    return out
