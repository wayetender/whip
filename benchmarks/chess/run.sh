#!/bin/sh

while [ ! -f /results/evernote/done ]
do
  sleep 2
done

mkdir -p /results/chess
python server.py > /results/chess/memory &
SERVER_PID=$!
sleep 4
echo "Starting tests (the output will stop for a while while tests are running...)"
shim python test.py > /results/chess/clientcalls
kill -2 $SERVER_PID
sleep 2
cp times /results/chess/times
cp bytes /results/chess/bytes

echo "Done"
touch /results/chess/done

