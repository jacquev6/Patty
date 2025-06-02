<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import deepCopy from 'deep-copy'
import { useRouter } from 'vue-router'

import { type LatestAdaptationBatch, type LlmModel, useAuthenticatedClient } from './apiClient'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import CreateAdaptationBatchFormInputsEditor from './CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  latestAdaptationBatch: LatestAdaptationBatch
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.latestAdaptationBatch.strategy))
const inputs = reactive<InputWithFile[]>(deepCopy(props.latestAdaptationBatch.inputs))
watch(
  () => props.latestAdaptationBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/adaptation/adaptation-batch', {
    body: {
      creator: identifiedUser.identifier,
      strategy,
      inputs: cleanedUpInputs.value,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'adaptation-batch', params: { id: response.data.id } })
  }
}

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.text.trim() !== '')
    .map(({ pageNumber, exerciseNumber, text }) => ({ pageNumber, exerciseNumber, text })),
)

const disabled = computed(() => {
  return strategy.settings.systemPrompt.trim() === '' || cleanedUpInputs.value.length === 0
})

const availableStrategySettings = computed(() => props.latestAdaptationBatch.availableStrategySettings)
</script>

<template>
  <BusyBox :busy>
    <ResizableColumns :columns="[1, 1]">
      <template #col-1>
        <p>Created by: <IdentifiedUser /></p>
        <AdaptationStrategyEditor :availableLlmModels :availableStrategySettings v-model="strategy" />
      </template>
      <template #col-2>
        <h1>Inputs</h1>
        <p><button @click="submit" :disabled>Submit</button></p>
        <CreateAdaptationBatchFormInputsEditor headers="h2" v-model="inputs" />
      </template>
    </ResizableColumns>
  </BusyBox>
</template>
