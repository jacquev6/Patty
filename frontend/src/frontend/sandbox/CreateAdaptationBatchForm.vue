<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import deepCopy from 'deep-copy'
import { useRouter } from 'vue-router'

import { type BaseAdaptationBatch, useAuthenticatedClient } from '@/apiClient'
import BusyBox from '@/BusyBox.vue'
import ResizableColumns from '@/ResizableColumns.vue'
import AdaptationStrategyEditor from '@/AdaptationStrategyEditor.vue'
import { useIdentifiedUserStore } from '@/IdentifiedUserStore'
import { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import CreateAdaptationBatchFormInputsEditor from './CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  baseAdaptationBatch: BaseAdaptationBatch
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.baseAdaptationBatch.strategy))
const inputs = reactive<InputWithFile[]>(deepCopy(props.baseAdaptationBatch.inputs))
watch(
  () => props.baseAdaptationBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/adaptation-batches', {
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

const availableStrategySettings = computed(() => props.baseAdaptationBatch.availableStrategySettings)
</script>

<template>
  <BusyBox :busy>
    <ResizableColumns :columns="[1, 1]">
      <template #col-1>
        <AdaptationStrategyEditor :availableStrategySettings :disabled="false" v-model="strategy" />
      </template>
      <template #col-2>
        <h1>Inputs</h1>
        <p><button @click="submit" :disabled>Submit</button></p>
        <CreateAdaptationBatchFormInputsEditor headers="h2" v-model="inputs" />
      </template>
    </ResizableColumns>
  </BusyBox>
</template>
