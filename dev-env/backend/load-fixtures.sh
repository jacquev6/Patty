#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


../docker-compose.sh exec backend-shell python -m patty load-fixtures "$@"
