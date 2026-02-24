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
import { ref, watch } from 'vue'

import CreateAdaptationBatchForm from './CreateAdaptationBatchForm.vue'
import { type BaseAdaptationBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import { useBreadcrumbsStore } from '@/frontend/basic/BreadcrumbsStore'

const props = defineProps<{
  base: string | null
}>()

const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

const identifiedUser = useIdentifiedUserStore()

const baseAdaptationBatch = ref<BaseAdaptationBatch | null>(null)

async function refresh() {
  const response = await client.GET('/api/base-adaptation-batch', {
    params: { query: { user: identifiedUser.identifier, base: props.base } },
  })
  if (response.data !== undefined) {
    baseAdaptationBatch.value = response.data
  }

  breadcrumbsStore.set([{ textKey: 'sandbox' }, { textKey: 'newAdaptationBatch', to: {} }])
}

watch(() => identifiedUser.identifier, refresh, { immediate: true })
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateAdaptationBatchForm v-if="baseAdaptationBatch !== null" :baseAdaptationBatch />
  </div>
</template>
