<script setup lang="ts">
import { onMounted, ref } from 'vue'

import CreateAdaptationForm from './CreateAdaptationForm.vue'
import { type LlmModel, type AdaptationStrategy, client, type AdaptationInput } from './apiClient'

const availableLlmModels = ref<LlmModel[]>([])

const defaultStrategy = ref<AdaptationStrategy | null>(null)

const defaultInput = ref<AdaptationInput | null>(null)

onMounted(async () => {
  const llmModelsPromise = client.GET('/api/available-llm-models')
  const latestStrategyPromise = client.GET('/api/adaptation/latest-strategy')
  const latestInputPromise = client.GET('/api/adaptation/latest-input')

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
})
</script>

<template>
  <CreateAdaptationForm
    v-if="availableLlmModels.length !== 0 && defaultStrategy !== null && defaultInput !== null"
    :availableLlmModels
    :defaultStrategy
    :defaultInput
  />
</template>
