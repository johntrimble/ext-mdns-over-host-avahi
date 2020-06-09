#!/usr/bin/env bash

set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

kubectl get service --all-namespaces --watch --output=json --output-watch-events=true | python3 "$SCRIPT_DIR"/update_mdns.py
