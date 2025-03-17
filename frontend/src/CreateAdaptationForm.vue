<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { type LlmModel, client } from './apiClient'
import assert from './assert'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  defaultSystemPrompt: string
  defaultInputText: string
}>()

const router = useRouter()

const availableLlmModels = computed(() => props.availableLlmModels)

assert(availableLlmModels.value.length !== 0)
const llmModel = ref<LlmModel>(availableLlmModels.value[0])
watch(availableLlmModels, (availableLlmModels) => {
  assert(availableLlmModels.length !== 0)
  llmModel.value = availableLlmModels[0]
})

const llmProviders = computed(() => {
  return [...new Set(availableLlmModels.value.map((model) => model.provider))]
})

const llmProvider = computed({
  get: () => {
    return llmModel.value?.provider ?? ''
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find((model) => model.provider === value)
    assert(model !== undefined)
    llmModel.value = model
  },
})

const llmNames = computed(() => {
  return availableLlmModels.value.filter((model) => model.provider === llmProvider.value).map((model) => model.name)
})

const llmName = computed({
  get: () => {
    return llmModel.value?.name ?? ''
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find(
      (model) => model.provider === llmModel.value?.provider && model.name === value,
    )
    assert(model !== undefined)
    llmModel.value = model
  },
})

const systemPrompt = ref(props.defaultSystemPrompt)
watch(
  () => props.defaultSystemPrompt,
  (defaultSystemPrompt) => {
    systemPrompt.value = defaultSystemPrompt
  },
)

const inputText = ref(props.defaultInputText)
watch(
  () => props.defaultInputText,
  (defaultInputText) => {
    inputText.value = defaultInputText
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  assert(llmModel.value !== null)

  const responsePromise = client.POST('/api/adaptation', {
    body: {
      llm_model: llmModel.value,
      system_prompt: systemPrompt.value,
      input_text: inputText.value,
    },
  })

  const response = await responsePromise
  busy.value = false

  if (response.data !== undefined) {
    router.push({ name: 'adaptation', params: { id: response.data.id } })
  }
}

const disabled = computed(() => {
  return systemPrompt.value.trim() === '' || inputText.value.trim() === ''
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <BusyBox :busy>
      <h1>LLM model</h1>
      <select v-model="llmProvider">
        <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option>
      </select>
      <select v-model="llmName">
        <option v-for="name in llmNames">{{ name }}</option>
      </select>
      <h1>System prompt</h1>
      <TextArea v-model="systemPrompt"></TextArea>
      <h1>Input text</h1>
      <TextArea v-model="inputText"></TextArea>
      <p><button @click="submit" :disabled>Submit</button></p>
    </BusyBox>
  </div>
</template>
