#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."


# Check cleanliness

if [ $(git branch --show-current) != main ]
then
  echo "Not on branch 'main'. Aborting."
  exit 1
fi

if [ "$(git ls-files --others --exclude-standard)" != "" ]
then
  git ls-files --others --exclude-standard
  echo "Untracked files. Aborting."
  exit 1
fi

if ! git diff --stat --exit-code
then
  echo "Unstaged changes. Aborting."
  exit 1
fi

if ! git diff --stat --staged --exit-code
then
  echo "Staged-but-not-committed changes will be included in publication commit. Press enter to continue, Ctrl+C to abort."
  read
fi

# Prepare

patty_version=$(date +%Y%m%d-%H%M%S)

migrations=backend/patty/migrations/versions
find $migrations -name '*_dev.py' \
| sed "s#$migrations/\(.*\)_dev\.py#\mv $migrations/\1_dev.py $migrations/\1_$patty_version.py#" \
| sh

git add .
git commit --allow-empty -m "Publish version $patty_version"

# Build and publish

prod/build.sh $patty_version push
git tag $patty_version
git push origin main --tags

# Continue working

git checkout develop
git merge main
git push origin develop
