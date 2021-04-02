#!/usr/bin/env bash
#
# Entrypoint
# Copyright API authors
#

set -e

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

python ${DIR}/api/migrate.py

exec "$@"
