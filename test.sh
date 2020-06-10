#!/usr/bin/env bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$SCRIPT_DIR"

vagrant up
vagrant ssh -- python3 /vagrant/update_mdns_test.py 

if [[ "$NO_CLEANUP" != "true" ]]; then
    vagrant destroy
fi

