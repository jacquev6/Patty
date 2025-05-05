<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef, watch } from 'vue'
import deepCopy from 'deep-copy'
import { useRouter } from 'vue-router'
import _ from 'lodash'
import * as zip from '@zip.js/zip.js'

import { type LatestBatch, type LlmModel, client } from './apiClient'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import assert from './assert'
import CreateBatchFormInputEditor, { type InputWithFile } from './CreateBatchFormInputEditor.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  latestBatch: LatestBatch
}>()

const router = useRouter()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.latestBatch.strategy))
const inputs = reactive<InputWithFile[]>(deepCopy(props.latestBatch.inputs))
watch(
  () => props.latestBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

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

  function parseFileName(fileName: string) {
    const match = fileName.match(/P(\d+)Ex(\d+)\.txt/)
    if (match === null) {
      return { pageNumber: null, exerciseNumber: null }
    }
    const pageNumber = parseInt(match[1])
    const exerciseNumber = match[2]
    return { pageNumber, exerciseNumber }
  }

  const fileInputs: InputWithFile[] = []
  for (let index = 0; index < files.length; index++) {
    const file = files.item(index)
    assert(file !== null)
    if (file.name.endsWith('.txt')) {
      const { pageNumber, exerciseNumber } = parseFileName(file.name)
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
          const { pageNumber, exerciseNumber } = parseFileName(entry.filename)
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

  inputs.splice(0, inputs.length, ...sortedInputs)
}

const editors = useTemplateRef<InstanceType<typeof CreateBatchFormInputEditor>[]>('editors')

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
    if (popped && editors.value !== null) {
      editors.value[inputs.length - 1].focus()
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

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.text.trim() !== '')
    .map(({ pageNumber, exerciseNumber, text }) => ({ pageNumber, exerciseNumber, text })),
)

const disabled = computed(() => {
  return strategy.settings.systemPrompt.trim() === '' || cleanedUpInputs.value.length === 0
})

const availableStrategySettings = computed(() => props.latestBatch.availableStrategySettings)
</script>

<template>
  <BusyBox :busy>
    <ResizableColumns :columns="[1, 1]">
      <template #col-1>
        <p>Created by: <IdentifiedUser /></p>
        <AdaptationStrategyEditor :availableLlmModels :availableStrategySettings v-model="strategy" />
      </template>
      <template #col-2>
        <h1>Inputs</h1>
        <p><button @click="submit" :disabled>Submit</button></p>
        <p>
          Open one or several text or zip files:
          <input data-cy="input-files" type="file" multiple="true" @change="openFiles" accept=".txt,.zip" />
        </p>
        <template v-for="index in inputs.length">
          <CreateBatchFormInputEditor ref="editors" :index v-model="inputs[index - 1]" />
        </template>
      </template>
    </ResizableColumns>
  </BusyBox>
</template>
