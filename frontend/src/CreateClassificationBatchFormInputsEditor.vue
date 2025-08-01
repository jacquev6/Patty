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
import Papa from 'papaparse'

import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputEditor from './CreateClassificationBatchFormInputEditor.vue'
import assert from './assert'

defineProps<{
  headers: string
}>()

const inputs = defineModel<InputWithFile[]>({ required: true })

async function openFile(event: Event) {
  const files = (event.target as HTMLInputElement).files
  assert(files !== null)
  assert(files.length === 1)
  const file = files.item(0)
  assert(file !== null)
  type Record = {
    id?: string
    page?: string
    num?: string
    instruction_hint_example: string
    statement: string
  }
  const records = await new Promise<Record[]>((resolve) =>
    Papa.parse<Record>(file, {
      header: true,
      dynamicTyping: false,
      skipEmptyLines: true,
      complete: function (results) {
        resolve(results.data)
      },
    }),
  )

  const fileInputs: InputWithFile[] = []
  for (const record of records) {
    const [pageNumber, exerciseNumber] = (() => {
      if (record.page !== undefined && record.num !== undefined) {
        return [Number.parseInt(record.page), record.num]
      } else {
        assert(record.id !== undefined)
        const idParts = record.id.split('_')
        assert(idParts.length === 2)
        assert(idParts[0].startsWith('p'))
        const pageNumber = Number.parseInt(idParts[0].slice(1))
        assert(idParts[1].startsWith('ex'))
        const exerciseNumber = idParts[1].slice(2)
        return [pageNumber, exerciseNumber]
      }
    })()

    assert(record.instruction_hint_example !== undefined)
    assert(record.statement !== undefined)

    fileInputs.push({
      inputFile: file.name,
      pageNumber,
      exerciseNumber,
      instructionHintExampleText: record.instruction_hint_example,
      statementText: record.statement,
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
  <p>
    Format: the file must be a tab-separated file, with fields <code>page</code>, <code>num</code>,
    <code>instruction_hint_example</code>, and <code>statement</code>. If fields <code>page</code> and
    <code>num</code> are not both present, the <code>id</code> field must be present and must be in the format
    <code>p{page}_ex{num}</code>.
  </p>
  <template v-for="index in inputs.length">
    <CreateClassificationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>
