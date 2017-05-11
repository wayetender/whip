#!/bin/sh

python server.py &
echo "Delaying for adapter startup..."
sleep 2
shim python test.py 
