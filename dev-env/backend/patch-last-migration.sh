#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

set -x

backup_to_load=s3://jacquev6/patty/prod/backups/patty-backup-20250422-062406.tar.gz

./shell.sh -c "python -m patty restore-database --yes --patch-according-to-settings $backup_to_load"
./alembic.sh upgrade 429d2fb463dd  # To be removed: only here because we have two migrations for next release. (Won't hurt until removed: will be no-op)

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
./alembic.sh upgrade head
