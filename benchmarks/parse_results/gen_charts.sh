#!/bin/sh
set -e

rm -rf /results/*
mkdir -p /results/evernote
mkdir -p /results/chess
mkdir -p /results/twitter

while [ ! -f /results/evernote/done ]
do
  sleep 2
done
while [ ! -f /results/chess/done ]
do
  sleep 2
done
while [ ! -f /results/twitter/done ]
do
  sleep 2
done


cd /results/twitter
CASE=twitter python /whip/parsing/parse.py > /results/network.tsv

cd /results/evernote
CASE=evernote python /whip/parsing/parse.py >> /results/network.tsv

cd /results/chess
CASE=chess python /whip/parsing/parse.py >> /results/network.tsv


cd /whip/parsing
mkdir -p /results/images
./plots.sh

echo ""
echo "---------------------------------"
echo "      Benchmarks Complete!       "
echo "---------------------------------"
echo ""
echo "Please check the results/images directory."
