#!/bin/bash
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

set -o errexit
set -o nounset
set -o pipefail

target=$1
command=$2

echo "Generating backend/generated/$target for the first time"
$command >generated/$target
echo Done

watchmedo shell-command \
  --command "test \${watch_event_type} = closed && echo 'Updating backend/generated/$target because \${watch_src_path} changed' && $command >generated/$target.tmp && mv generated/$target.tmp generated/$target && echo 'Done'" \
  --recursive --ignore-directories --ignore-patterns '*/__pycache__/*;patty/export/templates/*/index.html' \
  patty
