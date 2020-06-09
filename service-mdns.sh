#!/bin/sh
set -e -o pipefail
kubectl get service --all-namespaces --watch --output=json --output-watch-events=true | update_mdns.py