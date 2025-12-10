<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

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
import { useI18n } from 'vue-i18n'

import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputEditor from './CreateClassificationBatchFormInputEditor.vue'
import assert from '$/assert'
import WhiteSpace from '$/WhiteSpace.vue'

defineProps<{
  headers: string
}>()

const inputs = defineModel<InputWithFile[]>({ required: true })

const { t } = useI18n()

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

const tsvFileExtension = '.tsv'
const pageFieldName = 'page'
const numFieldName = 'num'
const idFieldName = 'id'
const idFieldFormat = 'p{page}_ex{num}'
const fields = [pageFieldName, numFieldName, 'instruction_hint_example', 'statement']
</script>

<template>
  <p>
    <I18nT keypath="openFile">
      <template #fileType>
        <code>{{ tsvFileExtension }}</code>
      </template>
    </I18nT>
    <WhiteSpace />
    <input data-cy="input-files" type="file" @change="openFile" accept=".tsv" />
  </p>
  <p>
    <I18nT keypath="format">
      <template #fields>
        <template v-for="(field, index) in fields">
          <template v-if="index === fields.length - 1">, {{ t('and') }}<WhiteSpace /></template>
          <template v-else-if="index !== 0">, </template>
          <code>{{ field }}</code>
        </template>
      </template>
    </I18nT>
    <WhiteSpace />
    <I18nT keypath="pageNumOrId">
      <template #pageName>
        <code>{{ pageFieldName }}</code>
      </template>
      <template #numName>
        <code>{{ numFieldName }}</code>
      </template>
      <template #idName>
        <code>{{ idFieldName }}</code>
      </template>
      <template #idFormat>
        <code>{{ idFieldFormat }}</code>
      </template>
    </I18nT>
  </p>
  <template v-for="index in inputs.length">
    <CreateClassificationBatchFormInputEditor ref="editors" :index :headers v-model="inputs[index - 1]" />
  </template>
</template>

<i18n>
en:
  openFile: "Open a {fileType} file:"
  format: "Format: the file must be a tab-separated file, with fields {fields}."
  and: and
  pageNumOrId: "If fields {pageName} and {numName} are not both present, the {idName} field must be present and must have format {idFormat}."
fr:
  openFile: "Ouvrir un fichier {fileType} :"
  format: "Format : le fichier doit être un fichier tabulé, avec les champs {fields}."
  and: et
  pageNumOrId: "Si les champs {pageName} et {numName} ne sont pas tous deux présents, le champ {idName} doit être présent et doit avoir le format {idFormat}."
</i18n>
