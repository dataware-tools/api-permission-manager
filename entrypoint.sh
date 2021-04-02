#!/usr/bin/env bash
#
# Entrypoint
# Copyright API authors
#

set -e

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

aerich upgrade

exec "$@"
