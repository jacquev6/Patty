#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

docker compose "$@"
