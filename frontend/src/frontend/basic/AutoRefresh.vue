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

<script setup lang="ts" generic="T extends { needsRefresh: boolean }">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useBreadcrumbsStore, type Breadcrumbs } from '@/frontend/basic/BreadcrumbsStore'
import BugMarker from '$/BugMarker.vue'

const props = defineProps<{
  reloadOnChanges: unknown
  load: () => Promise<T | null>
  breadcrumbs: (t: T) => Breadcrumbs
}>()

const { t } = useI18n()
const breadcrumbsStore = useBreadcrumbsStore()

type Status = { kind: 'loading' } | { kind: 'notFound' } | { kind: 'loaded'; val: T }

const data = ref<Status>({ kind: 'loading' })
let unmounted: boolean
let timerId: number | null

async function refresh() {
  timerId = null
  const val = await props.load()
  if (val === null) {
    data.value = { kind: 'notFound' }
  } else {
    data.value = { kind: 'loaded', val: val }
    if (val.needsRefresh && !unmounted) {
      timerId = window.setTimeout(refresh, 1000)
    }
  }
}

onMounted(() => {
  unmounted = false
  timerId = null
  refresh()
})

watch(
  () => props.reloadOnChanges,
  () => {
    if (!unmounted) {
      data.value = { kind: 'loading' }
      if (timerId !== null) {
        window.clearTimeout(timerId)
        timerId = null
      }
      refresh()
    }
  },
  { deep: true, immediate: false },
)

onUnmounted(() => {
  unmounted = true
  if (timerId !== null) {
    window.clearTimeout(timerId)
  }
})

watch(data, (data) => {
  if (data.kind === 'loaded') {
    // @todo Understand why this cast is necessary
    breadcrumbsStore.set(props.breadcrumbs(data.val as T))
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="data.kind === 'notFound'">
      <h1>{{ t('notFound') }}</h1>
    </template>
    <template v-else-if="data.kind === 'loaded'">
      <slot :data="data.val" :refresh></slot>
    </template>
    <template v-else-if="data.kind === 'loading'">
      <p>{{ t('loading') }}</p>
    </template>
    <BugMarker is="h1" v-else m="Unexpected state" :v="data" />
  </div>
</template>

<i18n>
en:
  notFound: Not found
  loading: Loading...
fr:
  notFound: Non trouvé
  loading: Chargement...
</i18n>
