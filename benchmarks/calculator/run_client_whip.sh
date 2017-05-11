#!/bin/sh

adapter adapter_client.yaml &
sleep 1
shim python client.py discovery 8000

