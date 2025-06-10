<script setup lang="ts">
import { ref, watch } from 'vue'

import CreateAdaptationBatchForm from './CreateAdaptationBatchForm.vue'
import { type AdaptationLlmModel, type LatestAdaptationBatch, useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const client = useAuthenticatedClient()

const availableAdaptationLlmModels = ref<AdaptationLlmModel[]>([])

const identifiedUser = useIdentifiedUserStore()

const latestAdaptationBatch = ref<LatestAdaptationBatch | null>(null)

async function refresh() {
  const availableAdaptationLlmModelsPromise = client.GET('/api/available-adaptation-llm-models')
  const latestAdaptationBatchPromise = client.GET('/api/latest-adaptation-batch', {
    params: { query: { user: identifiedUser.identifier } },
  })

  const availableAdaptationLlmModelsResponse = await availableAdaptationLlmModelsPromise
  if (availableAdaptationLlmModelsResponse.data !== undefined) {
    availableAdaptationLlmModels.value = availableAdaptationLlmModelsResponse.data
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
      v-if="availableAdaptationLlmModels.length !== 0 && latestAdaptationBatch !== null"
      :availableAdaptationLlmModels
      :latestAdaptationBatch
    />
  </div>
</template>
