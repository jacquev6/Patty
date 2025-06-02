<script lang="ts">
export function parseExerciseFileName(fileName: string) {
  const match = fileName.match(/P(\d+)Ex(\d+)\..*/)
  if (match === null) {
    return { pageNumber: null, exerciseNumber: null }
  }
  const pageNumber = parseInt(match[1])
  const exerciseNumber = match[2]
  return { pageNumber, exerciseNumber }
}
</script>

<script setup lang="ts">
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputEditor from './CreateClassificationBatchFormInputEditor.vue'
import assert from './assert'
import { useTemplateRef, watch } from 'vue'

defineProps<{
  headers: string
}>()

const inputs = defineModel<InputWithFile[]>({ required: true })

const editors = useTemplateRef<InstanceType<typeof CreateClassificationBatchFormInputEditor>[]>('editors')

watch(
  inputs,
  (inputs) => {
    if (
      inputs.length === 0 ||
      inputs[inputs.length - 1].instructionExampleHintText !== '' ||
      inputs[inputs.length - 1].statementText !== ''
    ) {
      inputs.push({ pageNumber: null, exerciseNumber: null, instructionExampleHintText: '', statementText: '' })
    }
    assert(inputs[inputs.length - 1].instructionExampleHintText === '')
    assert(inputs[inputs.length - 1].statementText === '')

    let popped = false
    while (
      inputs.length > 1 &&
      inputs[inputs.length - 2].instructionExampleHintText === '' &&
      inputs[inputs.length - 2].statementText === ''
    ) {
      inputs.pop()
      popped = true
    }
    if (popped && editors.value !== null) {
      editors.value[inputs.length - 1].focus()
    }
  },
  { deep: true, immediate: true },
)
</script>

<template>
  <!-- <p>
    @todo Open a tsv file:
    <input data-cy="input-files" type="file" @change="openFile" accept=".tsv" />
  </p> -->
  <template v-for="index in inputs.length">
    <CreateClassificationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>
