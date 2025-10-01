<script setup lang="ts">
import { type AdaptationBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditAdaptationBatchForm from './EditAdaptationBatchForm.vue'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/adaptation-batches/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ id }: AdaptationBatch) {
  return [{ textKey: 'sandbox' }, { textKey: 'existingAdaptationBatch', textArgs: { id }, to: {} }]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ id }" :load :breadcrumbs>
    <template v-slot="{ data: adaptationBatch }">
      <EditAdaptationBatchForm :adaptationBatch />
    </template>
  </AutoRefresh>
</template>
