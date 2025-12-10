#!/bin/bash
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


bash support/run.sh prod "$@"
