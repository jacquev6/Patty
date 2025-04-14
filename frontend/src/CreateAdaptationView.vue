<script setup lang="ts">
import { ref, watch } from 'vue'

import CreateAdaptationForm from './CreateAdaptationForm.vue'
import { type LlmModel, type AdaptationStrategy, client, type AdaptationInput } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const availableLlmModels = ref<LlmModel[]>([])

const identifiedUser = useIdentifiedUserStore()

const defaultStrategy = ref<AdaptationStrategy | null>(null)

const defaultInput = ref<AdaptationInput | null>(null)

async function refresh() {
  const llmModelsPromise = client.GET('/api/available-llm-models')
  const latestStrategyPromise = client.GET('/api/adaptation/latest-strategy', {
    params: { query: { user: identifiedUser.identifier } },
  })
  const latestInputPromise = client.GET('/api/adaptation/latest-input', {
    params: { query: { user: identifiedUser.identifier } },
  })

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }

  const latestStrategyResponse = await latestStrategyPromise
  if (latestStrategyResponse.data !== undefined) {
    defaultStrategy.value = latestStrategyResponse.data
  }

  const latestInputResponse = await latestInputPromise
  if (latestInputResponse.data !== undefined) {
    defaultInput.value = latestInputResponse.data
  }
}

watch(() => identifiedUser.identifier, refresh, { immediate: true })
</script>

<template>
  <CreateAdaptationForm
    v-if="availableLlmModels.length !== 0 && defaultStrategy !== null && defaultInput !== null"
    :availableLlmModels
    :defaultStrategy
    :defaultInput
  />
</template>
