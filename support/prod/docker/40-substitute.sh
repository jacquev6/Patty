#!/bin/sh
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

cp -r /usr/share/nginx/templates/frontend /usr/share/nginx/html/frontend

find /usr/share/nginx/templates/frontend -type f \
| sed -e 's|^/usr/share/nginx/templates/frontend/||' | \
while read f
do
  cat /usr/share/nginx/templates/frontend/$f \
  | sed -e "s|##TO_BE_SUBSTITUTED_UNAVAILABLE_UNTIL##|${PATTY_UNAVAILABLE_UNTIL}|g" \
  > /usr/share/nginx/html/frontend/$f
done
