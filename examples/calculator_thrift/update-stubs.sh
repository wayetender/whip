#!/bin/sh
BASEDIR=$(dirname $0)
thrift --gen py -out $BASEDIR/ $BASEDIR/calc.thrift
