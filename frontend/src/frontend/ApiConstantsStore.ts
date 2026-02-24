// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
