<script lang="ts">
export type InputWithFile = {
  pageNumber: number | null
  exerciseNumber: string | null
  inputFile?: string
  text: string
}
</script>

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'

import WhiteSpace from '$/WhiteSpace.vue'
import InputForNumberOrNull from '$/InputForNumberOrNull.vue'
import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import TextArea from '$/TextArea.vue'

defineProps<{
  headers: string
  index: number
}>()

const model = defineModel<InputWithFile>({ required: true })

const pageNumberProxy = computed({
  get: () => model.value.pageNumber,
  set: (value) => {
    model.value.pageNumber = value
    model.value.inputFile = undefined
  },
})

const exerciseNumberProxy = computed({
  get: () => model.value.exerciseNumber,
  set: (value) => {
    model.value.exerciseNumber = value
    model.value.inputFile = undefined
  },
})

const textProxy = computed({
  get: () => model.value.text,
  set: (value) => {
    model.value.text = value
    model.value.inputFile = undefined
  },
})

const textArea = useTemplateRef('textArea')

defineExpose({
  focus() {
    if (textArea.value !== null) {
      textArea.value.wrapped.focus()
    }
  },
})
</script>

<template>
  <component :is="headers">
    Input {{ index }}
    <template v-if="model.inputFile !== undefined">
      <span class="discreet">({{ model.inputFile }})</span>
    </template>
    <template v-if="model.text.trim() === ''">
      <WhiteSpace />
      <span class="discreet">(empty, ignored)</span>
    </template>
  </component>
  <p>
    Page: <InputForNumberOrNull data-cy="input-page-number" v-model="pageNumberProxy" />, exercise:
    <InputForNonEmptyStringOrNull data-cy="input-exercise-number" v-model="exerciseNumberProxy" />
  </p>
  <TextArea ref="textArea" data-cy="input-text" v-model="textProxy"></TextArea>
</template>

<style scoped>
.discreet {
  font-size: 70%;
  color: grey;
}
</style>
