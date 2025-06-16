<script setup lang="ts">
import { ref, watch } from 'vue'

import CreateAdaptationBatchForm from './CreateAdaptationBatchForm.vue'
import { type LatestAdaptationBatch, useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const latestAdaptationBatch = ref<LatestAdaptationBatch | null>(null)

async function refresh() {
  const latestAdaptationBatchPromise = client.GET('/api/latest-adaptation-batch', {
    params: { query: { user: identifiedUser.identifier } },
  })

  const latestAdaptationBatchResponse = await latestAdaptationBatchPromise
  if (latestAdaptationBatchResponse.data !== undefined) {
    latestAdaptationBatch.value = latestAdaptationBatchResponse.data
  }
}

watch(() => identifiedUser.identifier, refresh, { immediate: true })
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateAdaptationBatchForm v-if="latestAdaptationBatch !== null" :latestAdaptationBatch />
  </div>
</template>
