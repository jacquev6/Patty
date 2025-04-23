#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."


git clean $@ -xd .venv backend frontend dev-env/backend/pip-packages dev-env/frontend/cache dev-env/db/backups

git clean -nxd | sed 's/^Would remove/Kept/'
