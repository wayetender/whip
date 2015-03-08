#!/bin/sh

BASEDIR=$(dirname $0)
cd $BASEDIR
rm $BASEDIR/parser.pyc $BASEDIR/parser.out $BASEDIR/parsetab.py*
python $BASEDIR/parser.py

