<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthenticatedClient } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputsEditor from './CreateClassificationBatchFormInputsEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { useApiConstantsStore } from './ApiConstantsStore'
import classificationCamembert20250520 from './ClassificationCamembert20250520'
import { useI18n } from 'vue-i18n'

const { d } = useI18n({ useScope: 'global' })
const apiConstantsStore = useApiConstantsStore()
const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const runAdaptationAsString = ref('yes')

const llmModel = ref(apiConstantsStore.availableAdaptationLlmModels[0])

const runAdaptation = computed(() => runAdaptationAsString.value === 'yes')

const inputs = reactive<InputWithFile[]>([])

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.instructionHintExampleText.trim() !== '' || input.statementText.trim() !== '')
    .map(({ pageNumber, exerciseNumber, instructionHintExampleText, statementText }) => ({
      pageNumber,
      exerciseNumber,
      instructionHintExampleText,
      statementText,
    })),
)

const disabled = computed(() => cleanedUpInputs.value.length === 0)

async function submit() {
  const response = await client.POST('/api/classification-batches', {
    body: {
      creator: identifiedUser.identifier,
      inputs: cleanedUpInputs.value,
      modelForAdaptation: runAdaptation.value ? llmModel.value : null,
    },
  })
  if (response.data !== undefined) {
    router.push({ name: 'classification-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p>
    Classification model: <code>{{ classificationCamembert20250520.fileName }}</code
    >, provided by {{ classificationCamembert20250520.providedBy }} by e-mail on
    {{ d(classificationCamembert20250520.providedOn, 'long-date') }}
  </p>
  <p>
    Class names produced:
    <template v-for="(className, index) in classificationCamembert20250520.classesProduced">
      <template v-if="index !== 0">, </template>
      <code>{{ className }}</code>
    </template>
  </p>
  <p>
    Run adaptations after classification:
    <select data-cy="run-adaptation" v-model="runAdaptationAsString">
      <option>yes</option>
      <option>no</option>
    </select>
    <template v-if="runAdaptation">
      using
      <LlmModelSelector
        :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
        :disabled="false"
        v-model="llmModel"
      >
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each known exercise class.</template
    >
  </p>
  <h1>Inputs</h1>
  <p><button @click="submit" :disabled>Submit</button></p>
  <CreateClassificationBatchFormInputsEditor headers="h2" v-model="inputs" />
</template>
