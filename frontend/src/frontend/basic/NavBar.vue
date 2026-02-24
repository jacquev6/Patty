<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { useBreadcrumbsStore, type Breadcrumb } from '@/frontend/basic/BreadcrumbsStore'
import LocaleSelect from './NavBarLocaleSelect.vue'
import IdentifiedUser from './NavBarIdentifiedUser.vue'

const { t: tl } = useI18n()
const { t: tg } = useI18n({ useScope: 'global' })
const breadcrumbsStore = useBreadcrumbsStore()

function makeText(breadcrumb: Breadcrumb) {
  if (breadcrumb.textArgs === undefined) {
    return tg(breadcrumb.textKey)
  } else {
    return tg(breadcrumb.textKey, breadcrumb.textArgs)
  }
}
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px; display: flex; flex-direction: row">
    <div>
      <p>
        <RouterLink :to="{ name: 'index' }">{{ tl('home') }}</RouterLink>
        <template v-for="breadcrumb in breadcrumbsStore.breadcrumbs">
          &gt;
          <RouterLink v-if="breadcrumb.to !== undefined" :to="breadcrumb.to">{{ makeText(breadcrumb) }}</RouterLink>
          <template v-else>{{ makeText(breadcrumb) }}</template>
        </template>
      </p>
    </div>
    <div style="flex: 1; text-align: end">
      <p>
        <IdentifiedUser />
        <LocaleSelect />
      </p>
    </div>
  </div>
</template>

<style scoped>
div {
  background-color: rgb(210, 221, 238);
}

a {
  text-decoration: none;
  color: #007bff;
}
</style>

<i18n>
en:
  home: Malin home
fr:
  home: "Malin : accueil"
</i18n>
