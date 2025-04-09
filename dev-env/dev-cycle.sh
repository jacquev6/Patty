#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


skip_migration=""
cost_money=""
while [ $# -gt 0 ]; do
  case $1 in
    --skip-migration)
      skip_migration=--skip-migration
      ;;
    --cost-money)
      cost_money=--cost-money
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
  shift
done


backend/dev-cycle.sh $skip_migration $cost_money
frontend/dev-cycle.sh

if (cd ..; grep -n --color '\.only' -R frontend/e2e-tests)
then
  false
fi

./docker-compose.sh exec frontend-shell npx cypress run --e2e --browser electron
./docker-compose.sh exec frontend-shell npx cypress run --e2e --browser chromium
./docker-compose.sh exec frontend-shell npx cypress run --e2e --browser firefox
