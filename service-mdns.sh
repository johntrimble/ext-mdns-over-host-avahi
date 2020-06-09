#!/bin/sh
set -e -o pipefail
kubectl get service --all-namespaces --watch --output=json --output-watch-events=true | python3 update_mdns.py