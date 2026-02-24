// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import { defineStore } from 'pinia'
import { reactive } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

export type Breadcrumb = {
  textKey: string
  textArgs?: Record<string, string | number>
  to?: RouteLocationRaw
}
export type Breadcrumbs = Breadcrumb[]

export const useBreadcrumbsStore = defineStore('breadcrumbs', () => {
  const breadcrumbs = reactive<Breadcrumbs>([])

  function set(bs: Breadcrumbs) {
    breadcrumbs.splice(0, breadcrumbs.length, ...bs)
  }

  return {
    breadcrumbs,
    set,
  }
})
