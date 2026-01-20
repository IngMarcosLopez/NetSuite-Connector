#!/bin/sh

command -v poetry >/dev/null 2>&1 || { echo >&2 "I require poetry but it's not installed. Aborting."; exit 0; }

poetry export --without-hashes -n --without-urls | cut -f1 -d";" | sed 's/ *$//g' > requirements.txt
