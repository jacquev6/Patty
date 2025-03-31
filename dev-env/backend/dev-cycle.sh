#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


env_options=""
while [ $# -gt 0 ]; do
  case $1 in
    --long)
      env_options="$env_options --env PATTY_RUN_LONG_TESTS=true"
      ;;
    --cost-money)
      env_options="$env_options --env PATTY_RUN_TESTS_COSTING_MONEY=true"
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
  shift
done

./patch-last-migration.sh
./shell.sh -c "black . --line-length 120 --skip-magic-trailing-comma"
./shell.sh -c "mypy . --strict"
../docker-compose.sh exec $env_options backend-shell bash -c "python -m unittest discover --pattern '*.py'"
