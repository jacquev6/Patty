#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."


./docker-compose.sh exec --workdir /app/backend/patty backend-shell alembic "$@"
