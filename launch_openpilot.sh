#!/usr/bin/bash

while true; do rm -rf /data/params/d/LiveParameters; sleep 30; done &

exec ./launch_chffrplus.sh
