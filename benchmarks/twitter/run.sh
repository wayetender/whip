#!/bin/sh

while [ ! -f /results/chess/done ]
do
  sleep 2
done

mkdir -p /results/twitter
python server.py > /results/twitter/memory &
SERVER_PID=$!
sleep 2
echo "Starting tests (the output will stop for a while while tests are running...)"
shim python test.py > /results/twitter/clientcalls
kill -2 $SERVER_PID
sleep 2
cp times /results/twitter/times
cp bytes /results/twitter/bytes

echo "Done"
touch /results/twitter/done

