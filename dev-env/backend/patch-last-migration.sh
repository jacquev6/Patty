#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

set -x

rev_id_arg=
if [ -e ../../backend/patty/migrations/versions/*_dev.py ]
then
    ../docker-compose.sh exec --workdir /app/backend/patty backend-shell alembic downgrade head-1
  rev_id_arg="--rev-id $(find ../../backend/patty/migrations/versions/*_dev.py | sed -E 's#../../backend/patty/migrations/versions/(.*)_dev\.py#\1#')"
  rm -f ../../backend/patty/migrations/versions/*_dev.py
fi

../docker-compose.sh exec --workdir /app/backend/patty backend-shell alembic revision --autogenerate $rev_id_arg -m dev
../docker-compose.sh exec --workdir /app/backend/patty backend-shell alembic upgrade head

./shell.sh -c 'python -m patty load-fixtures dummy-adaptation-strategy'
