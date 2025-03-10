#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


./shell.sh -c "black . --line-length 120 --skip-magic-trailing-comma"
./shell.sh -c "mypy . --strict"
