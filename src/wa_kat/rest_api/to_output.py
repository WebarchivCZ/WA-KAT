#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import os.path
from os.path import join

from marcxml_parser import MARCXMLRecord

from bottle import post
from bottle import SimpleTemplate
from bottle_rest import form_to_params

from shared import API_PATH
from keywords import keyword_to_info

from ..convertors import mrc_to_marc

from conspectus import find_en_conspectus


# Variables ===================================================================
# Functions & classes =========================================================
def template_context(fn):
    return os.path.join(
        os.path.dirname(__file__),
        "../templates/",
        fn
    )


def template(fn):
    with open(template_context(fn)) as f:
        return f.read()


def compile_keywords(keywords):
    cz_keywords = []
    en_keywords = []
    for keyword in keywords:
        keyword = keyword_to_info(keyword)

        if not keyword:
            continue

        cz_keywords.append(
            {
                "uid": keyword["uid"],
                "zahlavi": keyword["zahlavi"],
                "zdroj": "czenas",
            }
        )
        if "angl_ekvivalent" in keyword:
            en_keywords.append({
                "zahlavi": keyword["angl_ekvivalent"],
                "zdroj": keyword.get("zdroj_angl_ekvivalentu") or "eczenas",
            })

    return cz_keywords, en_keywords


def render_mrc(data):
    template_body = template("sablona_katalogizace_eperiodika.mrc")

    return SimpleTemplate(template_body).render(**data)


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

    # convert to MRC format
    mrc = render_mrc(data).encode("utf-8")

    # create all output formats
    out = {
        "mrc": mrc,
        "oai": mrc_to_marc(mrc),
        # "dc": mrc_to_marc(mrc),
    }

    return out
