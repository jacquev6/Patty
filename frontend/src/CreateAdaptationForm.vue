<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type AdaptationInput, type AdaptationStrategy, type LlmModel, client } from './apiClient'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  defaultStrategy: AdaptationStrategy
  defaultInput: AdaptationInput
}>()

const router = useRouter()

const strategy = reactive(props.defaultStrategy) // WARNING: this does not react to changes in props.defaultStrategy

const input = reactive(props.defaultInput) // WARNING: this does not react to changes in props.defaultInput

const busy = ref(false)

async function submit() {
  busy.value = true

  const responsePromise = client.POST('/api/adaptation', {
    body: {
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
