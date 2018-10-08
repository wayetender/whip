#!/bin/sh
export LD_LIBRARY_PATH=/usr/local/lib
BASEDIR=$(dirname $0)
thrift -I $BASEDIR/../shim --gen py -out $BASEDIR/ $BASEDIR/protocol.thrift
thrift -gen py -out $BASEDIR/protocol $BASEDIR/../shim/clientprotocol.thrift
mkdir -p $BASEDIR/../shim/linux/gen-cpp
thrift -gen cpp -out $BASEDIR/../shim/linux/gen-cpp $BASEDIR/../shim/clientprotocol.thrift

