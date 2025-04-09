#!/bin/bash

set -o errexit
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


if [ -z $DISPLAY ]
then
  DISPLAY=:0 xhost +
  display_option="--env DISPLAY=host.docker.internal:0"
else
  xhost +
  display_option="--env DISPLAY"
fi

./docker-compose.sh exec --env PATTY_UNIT_TESTING=true $display_option frontend-shell npx cypress open
