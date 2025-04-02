#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


patty_version=$1
test -n "$patty_version"

action=$2
test "$action" == "push" -o "$action" == "load"

../dev-env/clean.sh -f

for part in $(grep 'AS final-' docker/Dockerfile | sed 's/.*AS final-//')
do
  echo $part
  echo $part | sed 's/./-/g'
  docker build \
    --pull \
    .. --file docker/Dockerfile --target final-$part \
    --build-arg PATTY_VERSION=$patty_version \
    --tag jacquev6/patty:$patty_version-$part

  if [ "$action" == "push" ]
  then
    docker push jacquev6/patty:$patty_version-$part
  fi
done
