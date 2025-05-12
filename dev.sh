#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


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
  rm -rf .venv
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements-dev.txt -r backend/requirements-run.txt
  cp backend/requirements-dev.txt backend/requirements-run.txt .venv/
fi

export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

. .venv/bin/activate

export PYTHONPATH=support

python -m tool dev "$@"
