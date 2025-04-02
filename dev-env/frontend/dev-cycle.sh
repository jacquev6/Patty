#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


./shell.sh -c "npm run format"
./shell.sh -c "npm run lint"
./shell.sh -c "npm run type-check"

if (cd ../..; git grep -n '\.only' -- frontend)
then
  false
fi

../docker-compose.sh exec --env PATTY_UNIT_TESTING=true frontend-shell npx cypress run --component --browser electron
../docker-compose.sh exec --env PATTY_UNIT_TESTING=true frontend-shell npx cypress run --component --browser chromium
../docker-compose.sh exec --env PATTY_UNIT_TESTING=true frontend-shell npx cypress run --component --browser firefox
