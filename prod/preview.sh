#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


ok=true
while read template
do
  file=${template%.template}
  if ! [ -f "$file" ]
  then
    echo "Please create '$file' according to '$template'"
    ok=false
  fi
done < <(find . -name '*.template')
$ok


./build.sh preview load

echo "Patty prod-preview: build"
./docker-compose.sh build
echo "Patty prod-preview: pull"
./docker-compose.sh pull --ignore-buildable

echo "Patty prod-preview: start"
./docker-compose.sh up --no-build --pull never --remove-orphans --detach
echo "Patty prod-preview: started (close with Ctrl+C)"
./docker-compose.sh logs --follow || true

echo "Patty prod-preview: clean-up"
./docker-compose.sh down --remove-orphans
./docker-compose.sh rm --stop --volumes --force
