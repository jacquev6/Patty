<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef, watch } from 'vue'
import deepCopy from 'deep-copy'
import { useRouter } from 'vue-router'

import { type LatestBatch, type LlmModel, client } from './apiClient'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import WhiteSpace from './WhiteSpace.vue'
import assert from './assert'
import InputForNumberOrNull from './InputForNumberOrNull.vue'
import InputForNonEmptyStringOrNull from './InputForNonEmptyStringOrNull.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  latestBatch: LatestBatch
}>()

const router = useRouter()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.latestBatch.strategy))
const inputs = reactive(deepCopy(props.latestBatch.inputs))
watch(
  () => props.latestBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

const textAreas = useTemplateRef<InstanceType<typeof TextArea>[]>('textAreas')

watch(
  inputs,
  () => {
    if (inputs.length === 0 || inputs[inputs.length - 1].text !== '') {
      inputs.push({ pageNumber: null, exerciseNumber: null, text: '' })
    }
    assert(inputs[inputs.length - 1].text === '')

    let popped = false
    while (inputs.length > 1 && inputs[inputs.length - 2].text === '') {
      inputs.pop()
      popped = true
    }
    if (popped && textAreas.value !== null) {
      textAreas.value[inputs.length - 1].wrapped.focus()
    }
  },
  { deep: true, immediate: true },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/adaptation/batch', {
    body: {
      creator: identifiedUser.identifier,
      strategy,
      inputs: cleanedUpInputs.value,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'batch', params: { id: response.data.id } })
  }
}

const cleanedUpInputs = computed(() => inputs.filter((input) => input.text.trim() !== ''))

const disabled = computed(() => {
  return strategy.systemPrompt.trim() === '' || cleanedUpInputs.value.length === 0
})
</script>

<template>
  <BusyBox :busy>
    <ResizableColumns :columns="[1, 1]">
      <template #col-1>
        <p>Created by: <IdentifiedUser /></p>
        <AdaptationStrategyEditor :availableLlmModels v-model="strategy" />
      </template>
      <template #col-2>
        <h1>Inputs</h1>
        <p><button @click="submit" :disabled>Submit</button></p>
        <template v-for="index in inputs.length">
          <h2>
            Input {{ index }}
            <template v-if="inputs[index - 1].text.trim() === ''">
              <WhiteSpace />
              <span class="ignored">(empty, ignored)</span>
            </template>
          </h2>
          <p>
            Page: <InputForNumberOrNull v-model="inputs[index - 1].pageNumber" />, exercise:
            <InputForNonEmptyStringOrNull v-model="inputs[index - 1].exerciseNumber" />
          </p>
          <TextArea ref="textAreas" id="input-text" data-cy="input-text" v-model="inputs[index - 1].text"></TextArea>
        </template>
      </template>
    </ResizableColumns>
  </BusyBox>
</template>

<style scoped>
.ignored {
  font-size: 70%;
  color: grey;
}
</style>
