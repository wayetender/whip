#!/bin/sh

BASEDIR=$(dirname $0)
cd $BASEDIR
source ../../env/adapter/bin/activate
rm parser.pyc parser.out parsetab.py*
python parser.py

