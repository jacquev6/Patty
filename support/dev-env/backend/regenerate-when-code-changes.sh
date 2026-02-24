#!/bin/bash
# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
