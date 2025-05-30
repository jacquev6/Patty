#!/bin/bash

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
  --recursive --ignore-directories --ignore-patterns '*/__pycache__/*;patty/adaptation/templates/*-export/index.html' \
  patty
