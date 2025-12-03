// A Pinia store for API responses that don't change during a user session

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { type ExtractionLlmModel, type AdaptationLlmModel, useAuthenticatedClient } from './ApiClient'

export const useApiConstantsStore = defineStore('api-constant', () => {
  const client = useAuthenticatedClient()

  const ready = ref(false)
  const availableExtractionLlmModels = ref<ExtractionLlmModel[]>([])
  const availableAdaptationLlmModels = ref<AdaptationLlmModel[]>([])
  const formalismsByAdaptationLlmModel = ref<Record<string, string[]>>({})

  ;(async () => {
    const availableExtractionLlmModelsPromise = client.GET('/api/available-extraction-llm-models')
    const availableAdaptationLlmModelsPromise = client.GET('/api/available-adaptation-llm-models')

    const availableExtractionLlmModelsResponse = await availableExtractionLlmModelsPromise
    if (availableExtractionLlmModelsResponse.data !== undefined) {
      availableExtractionLlmModels.value = availableExtractionLlmModelsResponse.data
    }

    const availableAdaptationLlmModelsResponse = await availableAdaptationLlmModelsPromise
    if (availableAdaptationLlmModelsResponse.data !== undefined) {
      availableAdaptationLlmModels.value = availableAdaptationLlmModelsResponse.data.map((x) => x[0])
      formalismsByAdaptationLlmModel.value = Object.fromEntries(
        availableAdaptationLlmModelsResponse.data.map((x) => [x[0].name, x[1]]),
      )
    }

    ready.value = true
  })()

  return {
    ready: computed(() => ready.value),
    availableExtractionLlmModels: computed(() => availableExtractionLlmModels.value),
    availableAdaptationLlmModels: computed(() => availableAdaptationLlmModels.value),
    formalismIsAvailableForAdaptationLlmModel(llmModel: AdaptationLlmModel, formalism: string) {
      return formalismsByAdaptationLlmModel.value[llmModel.name].includes(formalism)
    },
  }
})
