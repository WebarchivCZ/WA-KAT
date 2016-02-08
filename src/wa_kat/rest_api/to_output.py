#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import re
import json
import time
from os.path import join

from bottle import post
from bottle import SimpleTemplate
from bottle_rest import form_to_params

from shared import API_PATH
from shared import read_template

from keywords import keyword_to_info

from ..convertors import mrc_to_marc

from conspectus import find_en_conspectus


# Variables ===================================================================
# Functions & classes =========================================================
def compile_keywords(keywords):
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

        if "angl_ekvivalent" in keyword:
            en_keywords.append({
                "zahlavi": keyword["angl_ekvivalent"],
                "zdroj": keyword.get("zdroj_angl_ekvivalentu") or "eczenas",
            })

    return cz_keywords, en_keywords


def render_mrc(data):
    template_body = read_template("sablona_katalogizace_eperiodika.mrc")

    return SimpleTemplate(template_body).render(**data)


def url_to_fn(url):
    url = url.replace("http://", "").replace("https://", "")
    url = url.split("?")[0]

    return url.replace("%", "_").replace("/", "_")


def parse_date_range(date):
    """
    Parse input `date` string in free-text format for four-digit long groups.

    Args:
        date (str): Input containing years.

    Returns:
        tuple: ``(from, to)`` as four-digit strings.
    """
    NOT_ENDED = "9999"
    all_years = re.findall(r"\d{4}", date)

    if not all_years:
        return "****", NOT_ENDED

    elif len(all_years) == 1:
        return all_years[0], NOT_ENDED

    return all_years[0], all_years[1]


@post(join(API_PATH, "to_output"))
@form_to_params
def to_output(data):
    data = json.loads(data)

    # postprocessing
    if "keywords" in data:
        cz_keywords, en_keywords = compile_keywords(data["keywords"])
        del data["keywords"]

        data["cz_keywords"] = cz_keywords
        data["en_keywords"] = en_keywords

    data["annotation"] = data["annotation"].replace("\n", " ")
    data["en_conspect"] = find_en_conspectus(data["conspect"]["sub_code"])
    data["time"] = time  # for date generation

    # handle date range in the 008
    from_year, to_year = parse_date_range(data["creation_date"])
    data["from_year"] = from_year
    data["to_year"] = to_year

    # convert to MRC format
    mrc = render_mrc(data).encode("utf-8")

    # create all output formats
    out = {
        "fn": url_to_fn(data["url"]),
        "mrc": mrc,
        "oai": mrc_to_marc(mrc),
        # "dc": mrc_to_marc(mrc),
    }

    return out
