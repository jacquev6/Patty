#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

set -x

backup_to_load=s3://jacquev6/patty/prod/backups/patty-backup-20250512-051611.tar.gz

./shell.sh -c "python -m patty restore-database --yes --patch-according-to-settings $backup_to_load"

rev_id=
if [ -e ../../backend/patty/migrations/versions/*_dev.py ]
then
  rev_id="--rev-id $(find ../../backend/patty/migrations/versions/*_dev.py | sed -E 's#../../backend/patty/migrations/versions/(.*)_dev\.py#\1#')"
  rm -f ../../backend/patty/migrations/versions/*_dev.py
fi

current=$(./alembic.sh current | cut -d " " -f 1)
expected=$(./alembic.sh show head | grep "Rev:" | cut -d " " -f 2)

if [ "$current" != "$expected" ]
then
  echo "Current migration $current does not match expected migration $expected. Maybe you need to load a more recent backup?"
  exit 1
fi

./alembic.sh revision --autogenerate $rev_id -m dev

read -p "Check (and fix) the generated migration file. Press enter to continue"

./alembic.sh upgrade head
./shell.sh -c "python -m patty migrate-data"
