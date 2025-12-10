#!/bin/sh
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

cp -r /usr/share/nginx/templates/frontend /usr/share/nginx/html/frontend

find /usr/share/nginx/templates/frontend -type f \
| sed -e 's|^/usr/share/nginx/templates/frontend/||' | \
while read f
do
  cat /usr/share/nginx/templates/frontend/$f \
  | sed -e "s|##TO_BE_SUBSTITUTED_UNAVAILABLE_UNTIL##|${PATTY_UNAVAILABLE_UNTIL}|g" \
  > /usr/share/nginx/html/frontend/$f
done
