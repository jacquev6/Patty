#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


backend/dev-cycle.sh
frontend/dev-cycle.sh
