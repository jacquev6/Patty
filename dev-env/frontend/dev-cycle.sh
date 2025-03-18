#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


./shell.sh -c "npm run format"
./shell.sh -c "npm run lint"
./shell.sh -c "npm run type-check"
../docker-compose.sh exec --env PATTY_UNIT_TESTING=true frontend-shell bash -c "npm run test:unit"
