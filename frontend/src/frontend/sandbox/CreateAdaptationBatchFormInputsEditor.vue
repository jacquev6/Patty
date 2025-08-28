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
import _ from 'lodash'
import * as zip from '@zip.js/zip.js'

import CreateAdaptationBatchFormInputEditor, { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import assert from '@/assert'
import { useTemplateRef, watch } from 'vue'

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

async function openFiles(event: Event) {
  const files = (event.target as HTMLInputElement).files
  assert(files !== null)

  const fileInputs: InputWithFile[] = []
  for (let index = 0; index < files.length; index++) {
    const file = files.item(index)
    assert(file !== null)
    if (file.name.endsWith('.txt')) {
      const { pageNumber, exerciseNumber } = parseExerciseFileName(file.name)
      const text = await readFile(file)
      fileInputs.push({
        inputFile: file.name,
        pageNumber,
        exerciseNumber,
        text,
      })
    } else if (file.name.endsWith('.zip')) {
      const zipReader = new zip.ZipReader(new zip.BlobReader(file))
      for (const entry of await zipReader.getEntries()) {
        assert(entry.getData !== undefined)
        if (entry.filename.endsWith('.txt')) {
          const { pageNumber, exerciseNumber } = parseExerciseFileName(entry.filename)
          const text = await entry.getData(new zip.TextWriter())
          fileInputs.push({
            inputFile: `${entry.filename} in ${file.name}`,
            pageNumber,
            exerciseNumber,
            text,
          })
        }
      }
    }
  }

  const sortedInputs = _.sortBy(fileInputs, [
    'pageNumber',
    ({ exerciseNumber }) => {
      if (exerciseNumber === null) {
        return 0
      } else {
        const asNumber = parseInt(exerciseNumber)
        if (isNaN(asNumber)) {
          return 0
        } else {
          return asNumber
        }
      }
    },
    'exerciseNumber',
  ])

  inputs.value.splice(0, inputs.value.length, ...sortedInputs)
}

const editors = useTemplateRef<InstanceType<typeof CreateAdaptationBatchFormInputEditor>[]>('editors')

watch(
  inputs,
  (inputs) => {
    if (inputs.length === 0 || inputs[inputs.length - 1].text !== '') {
      inputs.push({ pageNumber: null, exerciseNumber: null, text: '' })
    }
    assert(inputs[inputs.length - 1].text === '')

    let popped = false
    while (inputs.length > 1 && inputs[inputs.length - 2].text === '') {
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
    Open one or several text or zip files:
    <input data-cy="input-files" type="file" multiple="true" @change="openFiles" accept=".txt,.zip" />
  </p>
  <template v-for="index in inputs.length">
    <CreateAdaptationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>
