<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script lang="ts">
export function parseExerciseFileName(fileName: string) {
  const match = fileName.match(/P(\d+)Ex(.+)\..*/)
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
import { useI18n } from 'vue-i18n'

import CreateAdaptationBatchFormInputEditor, { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import assert from '$/assert'
import { useTemplateRef, watch } from 'vue'

defineProps<{
  headers: string
}>()

const inputs = defineModel<InputWithFile[]>({ required: true })

const { t } = useI18n()

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
    {{ t('openFiles') }}
    <input data-cy="input-files" type="file" multiple="true" @change="openFiles" accept=".txt,.zip" />
  </p>
  <template v-for="index in inputs.length">
    <CreateAdaptationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>

<i18n>
en:
  openFiles: "Open one or several text or zip files:"
fr:
  openFiles: "Ouvrir un ou plusieurs fichiers texte ou zip :"
</i18n>
