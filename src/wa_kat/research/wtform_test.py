#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from wtforms import Form
from wtforms import BooleanField
from wtforms import StringField
from wtforms import DateTimeField
from wtforms import validators


# Variables ===================================================================
# Functions & classes =========================================================
class WAKatForm(Form):
    ISSN = StringField('ISSN', [validators.Length(min=4, max=25)])
    created = DateTimeField('Datum vzniku', format='%m.%d.%Y')


# Main program ================================================================
if __name__ == '__main__':
    form = WAKatForm()

    print unicode(form)
