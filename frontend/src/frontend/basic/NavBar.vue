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
  home: Patty home
fr:
  home: "Patty : accueil"
</i18n>
