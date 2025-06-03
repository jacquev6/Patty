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
import { useTemplateRef, watch } from 'vue'

import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputEditor from './CreateClassificationBatchFormInputEditor.vue'
import assert from './assert'

defineProps<{
  headers: string
}>()

const inputs = defineModel<InputWithFile[]>({ required: true })

function readFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      assert(typeof reader.result === 'string')
      resolve(reader.result)
    }
    reader.onerror = reject
    reader.readAsText(file)
  })
}

async function openFile(event: Event) {
  const files = (event.target as HTMLInputElement).files
  assert(files !== null)
  assert(files.length === 1)
  const file = files.item(0)
  assert(file !== null)
  assert(file.name.endsWith('.tsv'))
  const content = await readFile(file)
  const lines = content
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line !== '')
  const header = lines.shift()
  assert(header !== undefined)
  const fields = header.split('\t').map((field) => field.trim())
  const idIndex = fields.indexOf('id')
  assert(idIndex !== -1)
  const instructionIndex = fields.indexOf('instruction_hint_example')
  assert(instructionIndex !== -1)
  const statementIndex = fields.indexOf('statement')
  assert(statementIndex !== -1)

  const fileInputs: InputWithFile[] = []
  for (const line of lines) {
    const values = line.split('\t').map((value) => value.trim())
    assert(values.length === fields.length)
    const idParts = values[idIndex].split('_')
    assert(idParts.length === 2)
    assert(idParts[0].startsWith('p'))
    const pageNumber = Number.parseInt(idParts[0].slice(1))
    assert(idParts[1].startsWith('ex'))
    const exerciseNumber = idParts[1].slice(2)
    const instructionHintExampleText = values[instructionIndex]
    const statementText = values[statementIndex]
    fileInputs.push({
      inputFile: file.name,
      pageNumber,
      exerciseNumber,
      instructionHintExampleText,
      statementText,
    })
  }

  inputs.value.splice(0, inputs.value.length, ...fileInputs)
}

const editors = useTemplateRef<InstanceType<typeof CreateClassificationBatchFormInputEditor>[]>('editors')

watch(
  inputs,
  (inputs) => {
    if (
      inputs.length === 0 ||
      inputs[inputs.length - 1].instructionHintExampleText !== '' ||
      inputs[inputs.length - 1].statementText !== ''
    ) {
      inputs.push({ pageNumber: null, exerciseNumber: null, instructionHintExampleText: '', statementText: '' })
    }
    assert(inputs[inputs.length - 1].instructionHintExampleText === '')
    assert(inputs[inputs.length - 1].statementText === '')

    let popped = false
    while (
      inputs.length > 1 &&
      inputs[inputs.length - 2].instructionHintExampleText === '' &&
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
  <p>
    Open a <code>.tsv</code> file:
    <input data-cy="input-files" type="file" @change="openFile" accept=".tsv" />
  </p>
  <template v-for="index in inputs.length">
    <CreateClassificationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>
