<script lang="ts">
export type InputWithFile = {
  pageNumber: number | null
  exerciseNumber: string | null
  inputFile?: string
  instructionExampleHintText: string
  statementText: string
}
</script>

<script setup lang="ts">
import WhiteSpace from './WhiteSpace.vue'
import InputForNumberOrNull from './InputForNumberOrNull.vue'
import InputForNonEmptyStringOrNull from './InputForNonEmptyStringOrNull.vue'
import TextArea from './TextArea.vue'
import { computed, useTemplateRef } from 'vue'

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

const instructionExampleHintTextProxy = computed({
  get: () => model.value.instructionExampleHintText,
  set: (value) => {
    model.value.instructionExampleHintText = value
    model.value.inputFile = undefined
  },
})

const statementTextProxy = computed({
  get: () => model.value.statementText,
  set: (value) => {
    model.value.statementText = value
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
    <template v-if="model.instructionExampleHintText.trim() === '' && model.statementText.trim() === ''">
      <WhiteSpace />
      <span class="discreet">(empty, ignored)</span>
    </template>
  </component>
  <p>
    Page: <InputForNumberOrNull data-cy="input-page-number" v-model="pageNumberProxy" />, exercise:
    <InputForNonEmptyStringOrNull data-cy="input-exercise-number" v-model="exerciseNumberProxy" />
  </p>
  <p>Instruction, example, hint:</p>
  <TextArea ref="textArea" id="input-text" data-cy="input-text" v-model="instructionExampleHintTextProxy"></TextArea>
  <p>Statement:</p>
  <TextArea id="input-text" data-cy="input-text" v-model="statementTextProxy"></TextArea>
</template>

<style scoped>
.discreet {
  font-size: 70%;
  color: grey;
}
</style>
