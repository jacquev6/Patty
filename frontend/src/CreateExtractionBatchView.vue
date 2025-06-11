<script setup lang="ts">
import { ref, onMounted } from 'vue'

import CreateExtractionBatchForm from './CreateExtractionBatchForm.vue'
import {
  type ExtractionLlmModel,
  type ExtractionStrategy,
  type AdaptationLlmModel,
  useAuthenticatedClient,
} from './apiClient'

const client = useAuthenticatedClient()

const availableExtractionLlmModels = ref<ExtractionLlmModel[]>([])
const latestExtractionStrategy = ref<ExtractionStrategy | null>(null)
const extractionLlmResponseSchema = ref<Record<string, never>>({})
const availableAdaptationLlmModels = ref<AdaptationLlmModel[]>([])

onMounted(async () => {
  const availableExtractionLlmModelsPromise = client.GET('/api/available-extraction-llm-models')
  const latestExtractionStrategyPromise = client.GET('/api/latest-extraction-strategy')
  const extractionLlmResponseSchemaPromise = client.GET('/api/extraction-llm-response-schema')
  const availableAdaptationLlmModelsPromise = client.GET('/api/available-adaptation-llm-models')

  const availableExtractionLlmModelsResponse = await availableExtractionLlmModelsPromise
  if (availableExtractionLlmModelsResponse.data !== undefined) {
    availableExtractionLlmModels.value = availableExtractionLlmModelsResponse.data
  }

  const latestExtractionStrategyResponse = await latestExtractionStrategyPromise
  if (latestExtractionStrategyResponse.data !== undefined) {
    latestExtractionStrategy.value = latestExtractionStrategyResponse.data
  }

  const extractionLlmResponseSchemaResponse = await extractionLlmResponseSchemaPromise
  if (extractionLlmResponseSchemaResponse.data !== undefined) {
    extractionLlmResponseSchema.value = extractionLlmResponseSchemaResponse.data
  }

  const availableAdaptationLlmModelsResponse = await availableAdaptationLlmModelsPromise
  if (availableAdaptationLlmModelsResponse.data !== undefined) {
    availableAdaptationLlmModels.value = availableAdaptationLlmModelsResponse.data
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateExtractionBatchForm
      v-if="
        availableExtractionLlmModels.length !== 0 &&
        latestExtractionStrategy !== null &&
        Object.keys(extractionLlmResponseSchema).length !== 0 &&
        availableAdaptationLlmModels.length !== 0
      "
      :availableExtractionLlmModels
      :latestExtractionStrategy
      :extractionLlmResponseSchema
      :availableAdaptationLlmModels
    />
  </div>
</template>
