<script setup lang="ts">
import { ref, watch } from 'vue'

import CreateBatchForm from './CreateBatchForm.vue'
import { type LlmModel, type LatestBatch, useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const client = useAuthenticatedClient()

const availableLlmModels = ref<LlmModel[]>([])

const identifiedUser = useIdentifiedUserStore()

const latestBatch = ref<LatestBatch | null>(null)

async function refresh() {
  const llmModelsPromise = client.GET('/api/available-llm-models')
  const latestBatchPromise = client.GET('/api/adaptation/latest-batch', {
    params: { query: { user: identifiedUser.identifier } },
  })

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }

  const latestBatchResponse = await latestBatchPromise
  if (latestBatchResponse.data !== undefined) {
    latestBatch.value = latestBatchResponse.data
  }
}

watch(() => identifiedUser.identifier, refresh, { immediate: true })
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateBatchForm v-if="availableLlmModels.length !== 0 && latestBatch !== null" :availableLlmModels :latestBatch />
  </div>
</template>
