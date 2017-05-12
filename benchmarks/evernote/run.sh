#!/bin/sh

mkdir -p /results/evernote
python server.py > /results/evernote/memory &
SERVER_PID=$!
sleep 4
echo "Starting tests (the output will stop for a while while tests are running...)"
shim python test.py > /results/evernote/clientcalls
kill -2 $SERVER_PID
sleep 2
cp times /results/evernote/times
cp bytes /results/evernote/bytes

echo "Done"
touch /results/evernote/done

