#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


do_migration=true
cost_money=""
while [ $# -gt 0 ]; do
  case $1 in
    --skip-migration)
      do_migration=false
      ;;
    --cost-money)
      cost_money="--env PATTY_RUN_TESTS_COSTING_MONEY=true"
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
  shift
done

if $do_migration
then
  ./patch-last-migration.sh
fi

./shell.sh -c "black . --line-length 120 --skip-magic-trailing-comma"
./shell.sh -c "mypy . --strict"
../docker-compose.sh exec $cost_money backend-shell bash -c "python -m unittest discover --pattern '*.py'"
