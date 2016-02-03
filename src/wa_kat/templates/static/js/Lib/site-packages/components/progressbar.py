#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from browser import document


# Functions & classes =========================================================
class ProgressBar(object):
    tag = document["progress_bar"]
    whole_tag = document["whole_progress_bar"]
    original_message = tag.text

    @staticmethod
    def _compute_percentage(progress_tuple):
        # division by zero..
        if progress_tuple[0] == 0:
            return 0

        return (100 / progress_tuple[1]) * progress_tuple[0]

    @classmethod
    def show(cls, progress, msg=None):
        if cls.whole_tag.style.display == "none":
            cls.whole_tag.style.display = "block"

        percentage = cls._compute_percentage(progress)

        # toggle animation
        cls.tag.class_name = "progress-bar"
        if percentage < 100:
            cls.tag.class_name += " progress-bar-striped active"
        else:
            msg = "Hotovo"

        # show percentage in progress bar
        cls.tag.aria_valuemin = percentage
        cls.tag.style.width = "{}%".format(percentage)

        if msg:
            cls.tag.text = msg

    @classmethod
    def hide(cls):
        cls.whole_tag.style.display = "none"

    @classmethod
    def reset(cls):
        cls.hide()
        cls.tag.class_name = "progress-bar progress-bar-striped active"
        cls.tag.aria_valuemin = 0
        cls.tag.style.width = "{}%".format(0)
        cls.tag.text = cls.original_message
