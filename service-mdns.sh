#!/usr/bin/env bash

set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# kubectl will stop watching and exit with exit code 0 on occasion. When this
# happens just restart it. (https://github.com/kubernetes/kubernetes/issues/42552)
while true; do
    kubectl get service --all-namespaces --watch --output=json --output-watch-events=true \
    && sleep 5;
done | python3 "$SCRIPT_DIR"/update_mdns.py
