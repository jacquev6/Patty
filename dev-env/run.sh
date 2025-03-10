#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."


do_build=true
while [ $# -gt 0 ]
do
  case "$1" in
    --no-build)
      do_build=false
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
  shift
done

ok=true
while read template
do
  file=${template%.template}
  if ! [ -f "$file" ]
  then
    echo "Please create '$file' according to '$template'"
    ok=false
  fi
done < <(find . -name '*.template')
$ok

if ! (diff .venv/requirements-dev.txt backend/requirements-dev.txt && diff .venv/requirements-run.txt backend/requirements-run.txt) >/dev/null 2>&1
then
  echo "Patty dev-env: venv (for IDE completion only)"
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r backend/requirements-dev.txt -r backend/requirements-run.txt
  cp backend/requirements-dev.txt .venv/
  cp backend/requirements-run.txt .venv/
fi

cd dev-env

if $do_build
then
  echo "Patty dev-env: build"
  ./docker-compose.sh build
  echo "Patty dev-env: pull"
  ./docker-compose.sh pull --ignore-buildable
fi

echo "Patty dev-env: start"
./docker-compose.sh up --no-build --pull never --remove-orphans --detach
echo "Patty dev-env: started (close with Ctrl+C)"
./docker-compose.sh logs --follow || true

echo "Patty dev-env: clean-up"
./docker-compose.sh down --remove-orphans
./docker-compose.sh rm --stop --volumes --force
