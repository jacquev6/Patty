#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


# Outputs of actual runs of this script are in comments in https://github.com/jacquev6/Patty/issues/39
reference_batch_id=46
count=7

./docker-compose.sh exec backend-shell python -m patty restore-database --yes --patch-according-to-settings s3://jacquev6/patty/prod/backups/patty-backup-20250512-051611.tar.gz
./docker-compose.sh exec --workdir /app/backend/patty backend-shell alembic upgrade head
./docker-compose.sh stop submission-daemon

function investigate_issue_39() {
  time ./docker-compose.sh exec backend-shell python -m patty investigate-issue-39 $reference_batch_id $count $1 $2
  sleep 10
}

investigate_issue_39 1 1
investigate_issue_39 10 1
