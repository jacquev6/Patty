#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"


patty_version=$1
test -n "$patty_version"

action=$2
if [ "$action" == "push" ]
then
  platform=linux/amd64,linux/arm64
  push_load=--push
elif [ "$action" == "load" ]
then
  platform=linux/amd64
  push_load=--load
else
  exit 1
fi

../dev.sh clean --force

if ! docker buildx ls | grep patty-multi-platform-builder >/dev/null
then
  docker buildx create --name patty-multi-platform-builder
fi

for part in $(grep 'AS final-' docker/Dockerfile | sed 's/.*AS final-//')
do
  echo $part
  echo $part | sed 's/./-/g'
  docker buildx build \
    --pull \
    --builder patty-multi-platform-builder \
    .. --file docker/Dockerfile --target final-$part \
    --build-arg PATTY_VERSION=$patty_version \
    --tag jacquev6/patty:$patty_version-$part \
    --platform $platform \
    $push_load
done
