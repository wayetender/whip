#!/bin/sh
BASEDIR=$(dirname $0)
cd $BASEDIR
rm -f parser.pyc parser.out parsetab.py*
python parser.py

