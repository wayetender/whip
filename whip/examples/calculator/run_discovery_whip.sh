#!/bin/sh

adapter adapter_discovery.yaml &
sleep 1
shim python discovery.py 7999

