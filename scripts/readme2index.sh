#!/bin/sh

set -eu

tmpfile=$(mktemp)
trap 'rm -f $tmpfile' INT TERM EXIT

cp README.md "${tmpfile}"
sed -i -e '
/_TOC_/d
s#docs/##
' "${tmpfile}"
cp "${tmpfile}" $@
