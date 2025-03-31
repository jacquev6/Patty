<script setup lang="ts">
import { onMounted, ref } from 'vue'

import CreateAdaptationForm from './CreateAdaptationForm.vue'
import { type LlmModel, type AdaptationStrategy, client } from './apiClient'

const availableLlmModels = ref<LlmModel[]>([])

const defaultStrategy = ref<AdaptationStrategy | null>(null)

const defaultInputText = ref(`5 Complète avec "le vent" ou "la pluie"
a. Les feuilles sont chahutées par ...
b. Les vitres sont mouillées par ...
`)

onMounted(async () => {
  const latestStrategyPromise = client.GET('/api/adaptation/latest-strategy')
  const llmModelsPromise = client.GET('/api/available-llm-models')

  const latestStrategyResponse = await latestStrategyPromise
  if (latestStrategyResponse.data !== undefined) {
    defaultStrategy.value = latestStrategyResponse.data
  }

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }
})
</script>

<template>
  <CreateAdaptationForm
    v-if="availableLlmModels.length !== 0 && defaultStrategy !== null"
    :availableLlmModels
    :defaultStrategy
    :defaultInputText
  />
</template>
