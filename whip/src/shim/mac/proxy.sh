#!/bin/sh

BASEDIR=$(dirname $0)

export SHIM_CLIENT_PORT=9090 
export SHIM_CLIENT_ADDRESS=localhost 
export DYLD_INSERT_LIBRARIES=$BASEDIR/libshim.dylib 

$*
