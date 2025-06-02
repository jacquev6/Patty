<script setup lang="ts">
import { computed } from 'vue'

import { type LlmModel } from './apiClient'
import assert from './assert'
import WhiteSpace from './WhiteSpace.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  disabled: boolean
}>()

const model = defineModel<LlmModel>({ required: true })

assert(props.disabled || props.availableLlmModels.length !== 0)

const llmProviders = computed(() => {
  return [...new Set(props.availableLlmModels.map((llmModel) => llmModel.provider))]
})

const llmProvider = computed({
  get: () => {
    return model.value.provider
  },
  set: (value: string) => {
    const llmModel = props.availableLlmModels.find((llmModel) => llmModel.provider === value)
    assert(llmModel !== undefined)
    model.value = llmModel
  },
})

const llmNames = computed(() => {
  return props.availableLlmModels
    .filter((llmModel) => llmModel.provider === llmProvider.value)
    .map((llmModel) => llmModel.name)
})

const llmName = computed({
  get: () => {
    return model.value.name
  },
  set: (value: string) => {
    const llmModel = props.availableLlmModels.find(
      (llmModel) => llmModel.provider === model.value.provider && llmModel.name === value,
    )
    assert(llmModel !== undefined)
    model.value = llmModel
  },
})
</script>

<template>
  <template v-if="disabled">Provider: {{ model.provider }}, model: {{ model.name }}</template>
  <template v-else>
    <slot name="provider">Provider:</slot><WhiteSpace />
    <select data-cy="llm-provider" v-model="llmProvider">
      <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option></select
    ><slot name="model">, model:</slot><WhiteSpace />
    <select data-cy="llm-name" v-model="llmName">
      <option v-for="name in llmNames">{{ name }}</option>
    </select>
  </template>
</template>
