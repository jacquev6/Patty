<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as zip from '@zip.js/zip.js'
import _ from 'lodash'

import AddManualExercisesToPageFormInputEditor, {
  type InputWithFile,
} from './AddManualExercisesToPageFormInputEditor.vue'
import assert from '$/assert'
import { parseExerciseFileName } from '@/frontend/sandbox/CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  headers: string
  pageNumber: number
  exerciseClasses: string[]
}>()

const { t } = useI18n()

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
      if (pageNumber === props.pageNumber && exerciseNumber !== null) {
        const text = await readFile(file)
        fileInputs.push({
          inputFile: file.name,
          exerciseNumber,
          exerciseClass: null,
          text,
        })
      }
    } else if (file.name.endsWith('.zip')) {
      const zipReader = new zip.ZipReader(new zip.BlobReader(file))
      for (const entry of await zipReader.getEntries()) {
        assert(entry.getData !== undefined)
        if (entry.filename.endsWith('.txt')) {
          const { pageNumber, exerciseNumber } = parseExerciseFileName(entry.filename)
          if (pageNumber === props.pageNumber && exerciseNumber !== null) {
            const text = await entry.getData(new zip.TextWriter())
            fileInputs.push({
              inputFile: `${entry.filename} in ${file.name}`,
              exerciseNumber,
              exerciseClass: null,
              text,
            })
          }
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

const editors = useTemplateRef<InstanceType<typeof AddManualExercisesToPageFormInputEditor>[]>('editors')

watch(
  inputs,
  (inputs) => {
    if (inputs.length === 0 || inputs[inputs.length - 1].text !== '') {
      inputs.push({ exerciseNumber: null, exerciseClass: null, text: '' })
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
    {{ t('openFiles') }}
    <input data-cy="input-files" type="file" multiple="true" @change="openFiles" accept=".txt,.zip" />
  </p>
  <template v-for="index in inputs.length">
    <AddManualExercisesToPageFormInputEditor
      ref="editors"
      :index
      :headers
      :exerciseClasses
      v-model="inputs[index - 1]"
    />
  </template>
</template>

<i18n>
en:
  openFiles: "Open one or several text or zip files:"
fr:
  openFiles: "Ouvrir un ou plusieurs fichiers texte ou zip :"
</i18n>
