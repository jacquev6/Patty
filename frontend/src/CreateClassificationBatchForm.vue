<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type LlmModel, useAuthenticatedClient } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputsEditor from './CreateClassificationBatchFormInputsEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const props = defineProps<{
  availableLlmModels: LlmModel[]
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const runAdaptationAsString = ref('yes')

const llmModel = ref(props.availableLlmModels[0])

const runAdaptation = computed(() => runAdaptationAsString.value === 'yes')

const inputs = reactive<InputWithFile[]>([])

const busy = ref(false)

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.instructionExampleHintText.trim() !== '' || input.statementText.trim() !== '')
    .map(({ pageNumber, exerciseNumber, instructionExampleHintText, statementText }) => ({
      pageNumber,
      exerciseNumber,
      instructionExampleHintText,
      statementText,
    })),
)

async function submit() {
  busy.value = true
  const response = await client.POST('/api/classification-batches', {
    body: {
      creator: identifiedUser.identifier,
      strategy: {},
      inputs: cleanedUpInputs.value,
      modelForAdaptation: runAdaptation.value ? llmModel.value : null,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'classification-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p>
    Run adaptations after classification:
    <select data-cy="run-adaptation" v-model="runAdaptationAsString">
      <option>yes</option>
      <option>no</option>
    </select>
    <template v-if="runAdaptation">
      using
      <LlmModelSelector :availableLlmModels :disabled="false" v-model="llmModel">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each class.</template
    >
  </p>
  <h1>Inputs</h1>
  <p><button @click="submit">Submit</button></p>
  <!-- <p>@todo Open .tsv file</p> -->
  <CreateClassificationBatchFormInputsEditor headers="h2" v-model="inputs" />
</template>
