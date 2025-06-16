// A Pinia store for API responses that don't change during a user session

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { type ExtractionLlmModel, type AdaptationLlmModel, useAuthenticatedClient } from './apiClient'

export const useApiConstantsStore = defineStore('api-constant', () => {
  const client = useAuthenticatedClient()

  const ready = ref(false)
  const availableExtractionLlmModels = ref<ExtractionLlmModel[]>([])
  const availableAdaptationLlmModels = ref<AdaptationLlmModel[]>([])
  const extractionLlmResponseSchema = ref<Record<string, never>>({})

  ;(async () => {
    const availableExtractionLlmModelsPromise = client.GET('/api/available-extraction-llm-models')
    const availableAdaptationLlmModelsPromise = client.GET('/api/available-adaptation-llm-models')
    const extractionLlmResponseSchemaPromise = client.GET('/api/extraction-llm-response-schema')

    const availableExtractionLlmModelsResponse = await availableExtractionLlmModelsPromise
    if (availableExtractionLlmModelsResponse.data !== undefined) {
      availableExtractionLlmModels.value = availableExtractionLlmModelsResponse.data
    }

    const availableAdaptationLlmModelsResponse = await availableAdaptationLlmModelsPromise
    if (availableAdaptationLlmModelsResponse.data !== undefined) {
      availableAdaptationLlmModels.value = availableAdaptationLlmModelsResponse.data
    }

    const extractionLlmResponseSchemaResponse = await extractionLlmResponseSchemaPromise
    if (extractionLlmResponseSchemaResponse.data !== undefined) {
      extractionLlmResponseSchema.value = extractionLlmResponseSchemaResponse.data
    }

    ready.value = true
  })()

  return {
    ready: computed(() => ready.value),
    availableExtractionLlmModels: computed(() => availableExtractionLlmModels.value),
    availableAdaptationLlmModels: computed(() => availableAdaptationLlmModels.value),
    extractionLlmResponseSchema: computed(() => extractionLlmResponseSchema.value),
  }
})
