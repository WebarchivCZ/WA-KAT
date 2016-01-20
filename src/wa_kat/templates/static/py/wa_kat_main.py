#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import time

from browser import ajax
from browser import alert  # TODO: Remove
from browser import document

from view import ViewController
from components import ConspectHandler


# Varables ====================================================================
GUI_TO_REST_PERIODE = int(document["GUI_TO_REST_PERIODE"].html)


# Model =======================================================================
def make_request(url, data, on_complete):
    """
    Make AJAX request to `url` with given POST `data`. Call `on_complete`
    callback when complete.

    Args:
        url (str): URL.
        data (dict): Dictionary with POST data.
        on_complete (ref): Reference to function / method which will be called
            when the request is done.
    """
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('POST', url, True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send(data)


class AnalysisRunnerAdapter(object):
    @classmethod
    def on_complete(cls, req):
        # handle http errors
        if not (req.status == 200 or req.status == 0):
            ViewController.urlbox_error.show(req.text)
            return

        resp = json.loads(req.text)

        # handle structured errors
        if not resp["status"]:
            ViewController.urlbox_error.show(resp["error"])
            return

        # keep tracking of the progress
        if not resp["body"]["all_set"]:
            ViewController.progress_bar.show(resp["body"]["progress"])
            time.sleep(GUI_TO_REST_PERIODE)
            make_request(
                url="/api_v1/analyze",
                data={'url': ViewController.url},
                on_complete=cls.on_complete,
            )
            return

        # finally save the data to inputs
        ViewController.progress_bar.show(resp["body"]["progress"])
        ViewController.conspect_handler.set_new_conspect_dict(
            resp["conspect_dict"]
        )
        ViewController.log_view.add(resp["log"])

        obtained_data = json.dumps(resp["body"]["values"])
        ViewController.log_view.add("Obtained data: " + str(obtained_data))

        cls.fill_inputs(resp["body"]["values"])

    @staticmethod
    def fill_inputs(values):
        name_map = {  # TODO: get rid of this crap
            "title_tags": "title",
            "place_tags": "place",
            "lang_tags": "language",
            "keyword_tags": "keywords",
            "author_tags": "author",
            "annotation_tags": "annotation",
            "creation_dates": "creation_date",
        }

        for remote_name in values.keys():
            # special adapter for aleph keyword view
            if remote_name == "keyword_tags":
                adder = ViewController.analysis_kw_handler.add_keyword
                for keyword in values[remote_name]:
                    adder(keyword["val"])
                continue

            local_name = name_map.get(remote_name, remote_name)
            setattr(ViewController, local_name, values[remote_name])

    @classmethod
    def start(cls, ev):
        # reset all inputs
        ViewController.reset()

        # read the urlbox
        url = ViewController.url.strip()

        # make sure, that `url` was filled
        if not url:
            ViewController.urlbox_error.show("URL musí být vyplněna.")
            return

        ViewController.urlbox_error.hide()

        # normalize the `url`
        if not (url.startswith("http://") or url.startswith("http://")):
            url = "http://" + url
            ViewController.url = url  # store normalized url back to input

        make_request(
            url="/api_v1/analyze",
            data={'url': url},
            on_complete=cls.on_complete
        )


class AlephReaderAdapter(object):
    @classmethod
    def on_complete(cls, req):
        # handle http errors
        if not (req.status == 200 or req.status == 0):
            ViewController.issnbox_error.show(req.text)
            return

        resp = json.loads(req.text)

        if not resp:
            ViewController.issnbox_error.show(
                "Pro zadané ISSN nebyly nalezeny žádná data."
            )
            return

        if resp:
            dataset = resp[0]
            cls._handle_aleph_keyword_view(dataset)
            AnalysisRunnerAdapter.fill_inputs(dataset)

    @staticmethod
    def _handle_aleph_keyword_view(dataset):
        # redirect the keywords to Aleph view
        adder = ViewController.aleph_kw_handler.add_keyword
        for keyword in dataset.get("keyword_tags", []):
            adder(keyword["val"])

        if "keyword_tags" in dataset:
            del dataset["keyword_tags"]

    @classmethod
    def start(cls, ev):
        # InputMapper.reset()  # TODO: implement
        ViewController.issnbox_error.reset()
        issn = ViewController.issn.strip()

        # make sure, that `issn` was filled
        if not issn:
            ViewController.issnbox_error.show("ISSN nebylo vyplněno!")
            return

        ViewController.issnbox_error.hide()

        make_request(
            url="/api_v1/aleph",
            data={'issn': issn},
            on_complete=cls.on_complete
        )


class MARCGeneratorAdapter(object):
    @classmethod
    def on_complete(cls, req):
        # handle http errors
        if not (req.status == 200 or req.status == 0):
            alert(req.text)  # better handling
            return

        resp = json.loads(req.text)

        if not resp:
            alert("Chyba při konverzi!")  # TODO: better
            return

        if resp:
            pass  # TODO: do something
            alert(resp)

    @staticmethod
    def _read_dataset():
        return ViewController.get_all_properties()

    @classmethod
    def start(cls, ev):
        ev.stopPropagation()
        make_request(
            url="/api_v1/to_marc",
            data={"data": json.dumps(cls._read_dataset())},
            on_complete=cls.on_complete
        )


def func_on_enter(func):
    def function_after_enter_pressed(ev):
        ev.stopPropagation()

        # if the key was `enter` ..
        if ev.keyCode == 13:
            func(ev)

    return function_after_enter_pressed


def set_periodicity():
    periodes = document["default_periode"].innerHTML

    ViewController.periodicity = periodes.splitlines()


# bind buttons to actions
document["run_button"].bind("click", AnalysisRunnerAdapter.start)
document["url"].bind("keypress", func_on_enter(AnalysisRunnerAdapter.start))
document["issn_run_button"].bind("click", AlephReaderAdapter.start)
document["issn"].bind("keypress", func_on_enter(AlephReaderAdapter.start))
document["marc_button"].bind("click", MARCGeneratorAdapter.start)
ConspectHandler.set_new_conspect_dict(
    json.loads(document["default_konspekt"].innerHTML)
)
set_periodicity()
AnalysisRunnerAdapter.start(1)
