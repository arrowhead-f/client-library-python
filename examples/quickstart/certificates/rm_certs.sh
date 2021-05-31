#!/bin/bash

# Removes all keystores, certificates and truststores potentially created by
# `mk_certs.sh`.

cd "$(dirname "$0")" || exit
find . -regex ".*\.\(p12\|crt\|jks\|pub\|key\|ca\)" -exec rm -f {} \;
