#!/bin/sh

adapter adapter_adder.yaml &

sleep 5

shim python adder.py adder 8001 discovery 8000
