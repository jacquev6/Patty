<script setup lang="ts">
import { type ClassificationBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditClassificationBatchForm from './EditClassificationBatchForm.vue'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/classification-batches/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ id }: ClassificationBatch) {
  return [{ textKey: 'sandbox' }, { textKey: 'existingClassificationBatch', textArgs: { id }, to: {} }]
}
</script>

<template>
  <AutoRefresh :load :breadcrumbs>
    <template v-slot="{ data: classificationBatch, refresh }">
      <EditClassificationBatchForm :classificationBatch @batchUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
