<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import deepCopy from 'deep-copy'

import { type AdaptationInput, type AdaptationStrategy, type LlmModel, client } from './apiClient'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  defaultStrategy: AdaptationStrategy
  defaultInput: AdaptationInput
}>()

const router = useRouter()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.defaultStrategy))
watch(
  () => props.defaultStrategy,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue))
  },
)

const input = reactive(deepCopy(props.defaultInput))
watch(
  () => props.defaultInput,
  (newValue) => {
    Object.assign(input, deepCopy(newValue))
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  const responsePromise = client.POST('/api/adaptation', {
    body: {
      creator: identifiedUser.identifier,
      strategy,
      input,
    },
  })

  const response = await responsePromise
  busy.value = false

  if (response.data !== undefined) {
    router.push({ name: 'adaptation', params: { id: response.data.id } })
  }
}

const disabled = computed(() => {
  return strategy.systemPrompt.trim() === '' || input.text.trim() === ''
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <BusyBox :busy>
      <ResizableColumns :columns="2">
        <template #col-1>
          <p>Created by: <IdentifiedUser /></p>
          <AdaptationStrategyEditor :availableLlmModels v-model="strategy" />
        </template>
        <template #col-2>
          <h1>Input text</h1>
          <TextArea data-cy="input-text" v-model="input.text"></TextArea>
          <p><button @click="submit" :disabled>Submit</button></p>
        </template>
      </ResizableColumns>
    </BusyBox>
  </div>
</template>
