<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import EditExtractionBatchForm from './EditExtractionBatchForm.vue'
import { type ExtractionBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/extraction-batches/{id}`, { params: { path: { id: props.id } } })
  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ id }: ExtractionBatch) {
  return [{ textKey: 'sandbox' }, { textKey: 'existingExtractionBatch', textArgs: { id }, to: {} }]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ id }" :load :breadcrumbs>
    <template v-slot="{ data: extractionBatch, refresh }">
      <EditExtractionBatchForm :extractionBatch @batchUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
