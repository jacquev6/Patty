<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import CreateAdaptationBatchFormInputsEditor from './CreateAdaptationBatchFormInputsEditor.vue'
import { type Textbook, useAuthenticatedClient } from './apiClient'
import assert from './assert'
import { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { useApiConstantsStore } from './ApiConstantsStore'

const props = defineProps<{
  textbookId: string
  availableStrategySettings: string[]
}>()

const emit = defineEmits<{
  (e: 'textbook-updated', textbook: Textbook): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()
const apiConstantsStore = useApiConstantsStore()

const identifiedUser = useIdentifiedUserStore()

const availableAdaptationLlmModels = computed(() => apiConstantsStore.availableAdaptationLlmModels)

const model = ref(availableAdaptationLlmModels.value[0])

assert(availableAdaptationLlmModels.value.length !== 0)

const llmProviders = computed(() => {
  return [...new Set(availableAdaptationLlmModels.value.map((model) => model.provider))]
})

const llmProvider = computed({
  get: () => {
    return model.value.provider
  },
  set: (value: string) => {
    const m = availableAdaptationLlmModels.value.find((m) => m.provider === value)
    assert(m !== undefined)
    model.value = m
  },
})

const llmNames = computed(() => {
  return availableAdaptationLlmModels.value
    .filter((model) => model.provider === llmProvider.value)
    .map((model) => model.name)
})

const llmName = computed({
  get: () => {
    return model.value.name
  },
  set: (value: string) => {
    const m = availableAdaptationLlmModels.value.find((m) => m.provider === model.value.provider && m.name === value)
    assert(m !== undefined)
    model.value = m
  },
})

const inputs = reactive<InputWithFile[]>([])

const noStrategySettings = '-- choose --'
const strategySettings = ref(noStrategySettings)

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/textbooks/{id}/adaptation-batches', {
    params: { path: { id: props.textbookId } },
    body: {
      creator: identifiedUser.identifier,
      model: model.value,
      branchName: strategySettings.value,
      inputs: cleanedUpInputs.value,
    },
  })
  busy.value = false
  inputs.length = 0
  strategySettings.value = noStrategySettings
  if (response.data !== undefined) {
    emit('textbook-updated', response.data)
  }
}

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.text.trim() !== '')
    .map(({ pageNumber, exerciseNumber, text }) => ({ pageNumber, exerciseNumber, text })),
)

const disabled = computed(() => {
  return cleanedUpInputs.value.length === 0 || strategySettings.value === noStrategySettings
})
</script>

<template>
  <p>{{ t('createdBy') }} <IdentifiedUser /></p>
  <p>
    {{ t('llmProvider') }}
    <select data-cy="llm-provider" v-model="llmProvider">
      <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option></select
    >,
    {{ t('model') }}
    <select data-cy="llm-name" v-model="llmName">
      <option v-for="name in llmNames">{{ name }}</option></select
    >,
    {{ t('strategySettings') }}
    <select data-cy="strategy-settings" v-model="strategySettings">
      <option :value="noStrategySettings">{{ noStrategySettings }}</option>
      <option v-for="setting in availableStrategySettings">{{ setting }}</option>
    </select>
  </p>
  <p>
    <button @click="submit" :disabled>{{ t('submit') }}</button>
  </p>
  <CreateAdaptationBatchFormInputsEditor headers="h3" v-model="inputs" />
</template>

<i18n>
en:
  createdBy: "Created by:"
  llmProvider: "LLM provider:"
  model: "model:"
  strategySettings: "strategy settings:"
  submit: Submit
fr:
  createdBy: "Créé par :"
  llmProvider: "Fournisseur LLM :"
  model: "modèle :"
  strategySettings: "paramètres de stratégie :"
  submit: Soumettre
</i18n>
