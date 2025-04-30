#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset
cd "$(dirname "${BASH_SOURCE[0]}")/../.."


mv frontend/cypress-image-diff-screenshots/comparison/*.png frontend/cypress-image-diff-screenshots/baseline/
