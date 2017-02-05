#! /usr/bin/env sh
export PYTHONPATH="src/:$PYTHONPATH"

python2 -m pytest tests $@