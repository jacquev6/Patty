<script setup lang="ts">
import { ref, watch } from 'vue'

import CreateAdaptationBatchForm from './CreateAdaptationBatchForm.vue'
import { type LlmModel, type LatestAdaptationBatch, useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const client = useAuthenticatedClient()

const availableLlmModels = ref<LlmModel[]>([])

const identifiedUser = useIdentifiedUserStore()

const latestAdaptationBatch = ref<LatestAdaptationBatch | null>(null)

async function refresh() {
  const llmModelsPromise = client.GET('/api/available-llm-models')
  const latestAdaptationBatchPromise = client.GET('/api/latest-adaptation-batch', {
    params: { query: { user: identifiedUser.identifier } },
  })

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }

  const latestAdaptationBatchResponse = await latestAdaptationBatchPromise
  if (latestAdaptationBatchResponse.data !== undefined) {
    latestAdaptationBatch.value = latestAdaptationBatchResponse.data
  }
}

watch(() => identifiedUser.identifier, refresh, { immediate: true })
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateAdaptationBatchForm
      v-if="availableLlmModels.length !== 0 && latestAdaptationBatch !== null"
      :availableLlmModels
      :latestAdaptationBatch
    />
  </div>
</template>
