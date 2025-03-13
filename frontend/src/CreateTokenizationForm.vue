<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { type PostTokenizationRequest, client } from './apiClient'
import assert from './assert'
import { useRouter } from 'vue-router'

const props = defineProps<{
  availableLlmModels: PostTokenizationRequest['llm_model'][]
  defaultSystemPrompt: string
  defaultInputText: string
}>()

const router = useRouter()

const availableLlmModels = computed(() => props.availableLlmModels)

assert(availableLlmModels.value.length !== 0)
const llmModel = ref<PostTokenizationRequest['llm_model']>(availableLlmModels.value[0])

watch(availableLlmModels, (availableLlmModels) => {
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

const disabled = ref(false)

async function submit() {
  disabled.value = true

  assert(llmModel.value !== null)

  const responsePromise = client.POST('/api/tokenization', {
    body: {
      llm_model: llmModel.value,
      system_prompt: systemPrompt.value,
      input_text: inputText.value,
    },
  })

  const response = await responsePromise
  disabled.value = false

  if (response.data !== undefined) {
    router.push({ name: 'tokenization', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>LLM provider and model name</h1>
  <select v-model="llmProvider" :disabled>
    <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option>
  </select>
  <select v-model="llmName" :disabled>
    <option v-for="name in llmNames">{{ name }}</option>
  </select>
  <h1>System prompt</h1>
  <textarea v-model="systemPrompt" rows="15" cols="120" :disabled></textarea>
  <h1>Input text</h1>
  <textarea v-model="inputText" rows="10" cols="120" :disabled></textarea>
  <p><button @click="submit" :disabled>Submit</button></p>
</template>
