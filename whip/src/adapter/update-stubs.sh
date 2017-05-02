#!/bin/sh
BASEDIR=$(dirname $0)
thrift -I $BASEDIR/../shim --gen py -out $BASEDIR/ $BASEDIR/protocol.thrift
thrift -gen py -out $BASEDIR/protocol $BASEDIR/../shim/clientprotocol.thrift

