<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed, reactive, ref } from 'vue'

import { useAuthenticatedClient, type AdaptationLlmModel } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '../basic/IdentifiedUserStore'
import { useApiConstantsStore } from '../ApiConstantsStore'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import AddManualExercisesToPageFormInputsEditor from './AddManualExercisesToPageFormInputsEditor.vue'
import type { InputWithFile } from './AddManualExercisesToPageFormInputEditor.vue'
import assert from '$/assert'

const props = defineProps<{
  textbookId: string
  pageNumber: number
  exerciseClasses: string[]
}>()

const router = useRouter()
const { t } = useI18n()
const client = useAuthenticatedClient()
const identifiedUser = useIdentifiedUserStore()
const apiConstantsStore = useApiConstantsStore()

const modelForAdaptation = ref<AdaptationLlmModel>(apiConstantsStore.availableAdaptationLlmModels[0])

const inputs = reactive<InputWithFile[]>([])

const filteredInputs = computed(() => inputs.filter((input) => input.text.trim() !== ''))

const disabled = computed(
  () =>
    filteredInputs.value.length === 0 ||
    filteredInputs.value.find(
      ({ exerciseNumber, exerciseClass }) => exerciseNumber === null || exerciseClass === null,
    ) !== undefined,
)

async function submit() {
  await client.POST('/api/textbooks/{textbook_id}/manual-exercises-chunks', {
    params: { path: { textbook_id: props.textbookId } },
    body: {
      creator: identifiedUser.identifier,
      modelForAdaptation: modelForAdaptation.value,
      exercises: filteredInputs.value.map(({ exerciseNumber, exerciseClass, text }) => {
        assert(exerciseNumber !== null)
        assert(exerciseClass !== null)
        return {
          pageNumber: props.pageNumber,
          exerciseNumber,
          exerciseClass,
          fullText: text,
        }
      }),
    },
  })
  router.push({ name: 'textbook-page', params: { textbookId: props.textbookId, pageNumber: props.pageNumber } })
}
</script>

<template>
  <h1>{{ t('llmModel') }}</h1>
  <p>
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
      :disabled="false"
      v-model="modelForAdaptation"
    >
      <template #provider>{{ t('modelForAdaptation') }}</template>
    </LlmModelSelector>
  </p>
  <h1>{{ t('inputs') }}</h1>
  <p>
    <button :disabled @click="submit">{{ t('submit') }}</button>
  </p>
  <AddManualExercisesToPageFormInputsEditor headers="h2" :exerciseClasses v-model="inputs" />
</template>

<i18n lang="yaml">
en:
  submit: Submit
  llmModel: 'LLM Model'
  modelForAdaptation: 'Model provider for adaptation:'
  inputs: Inputs
fr:
  submit: Soumettre
  llmModel: 'Modèle LLM'
  modelForAdaptation: "Fournisseur de modèle pour l'adaptation :"
  inputs: Entrées
</i18n>
