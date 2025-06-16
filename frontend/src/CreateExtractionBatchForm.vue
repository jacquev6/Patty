<script setup lang="ts">
import { computed, reactive, ref, shallowRef, watch } from 'vue'
import { useRouter } from 'vue-router'
import shajs from 'sha.js'
import { computedAsync } from '@vueuse/core'
import deepCopy from 'deep-copy'

import pdfjs, { type PDFDocumentProxy } from './pdfjs'
import { type ExtractionStrategy, useAuthenticatedClient } from './apiClient'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import assert from './assert'
import PdfPageRenderer from './PdfPageRenderer.vue'
import PdfNavigationControls from './PdfNavigationControls.vue'
import LlmModelSelector from './LlmModelSelector.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from './TextArea.vue'
import { useApiConstantsStore } from './ApiConstantsStore'

const props = defineProps<{
  latestExtractionStrategy: ExtractionStrategy
}>()

const router = useRouter()

const client = useAuthenticatedClient()
const apiConstantsStore = useApiConstantsStore()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.latestExtractionStrategy))
watch(
  () => props.latestExtractionStrategy,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue))
  },
)

const runClassificationAsString = ref('yes')
const runClassification = computed(() => runClassificationAsString.value === 'yes')

const runAdaptationAsString = ref('yes')
const modelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])
const runAdaptation = computed(() => runClassification.value && runAdaptationAsString.value === 'yes')

const uploading = ref(false)
const uploadedFileSha256 = ref<string | null>(null)
const document = shallowRef<PDFDocumentProxy | null>(null)
const firstPageNumber = ref(1)
const lastPageNumber = ref(1)

const disabled = computed(
  () =>
    uploadedFileSha256.value === null ||
    firstPageNumber.value < 1 ||
    lastPageNumber.value < firstPageNumber.value ||
    lastPageNumber.value > (document.value?.numPages ?? 0),
)

async function openFile(event: Event) {
  uploadedFileSha256.value = null

  const input = event.target as HTMLInputElement
  assert(input.files !== null)
  if (input.files.length == 1) {
    const file = input.files[0]
    const data = await file.arrayBuffer()

    const startTime = performance.now()
    const documentTask = pdfjs.getDocument({ data })
    const sha256 = shajs('sha256').update(new Uint8Array(data)).digest('hex')
    console.info(`Computed sha256 for ${file.name} in ${Math.round(performance.now() - startTime)}ms: ${sha256}`)
    // We could use documentTask.onProgress to report progress to the user
    document.value = await documentTask.promise
    console.info(`Loaded ${file.name} in ${Math.round(performance.now() - startTime)}ms`)

    firstPageNumber.value = 1
    lastPageNumber.value = document.value.numPages

    const response = await client.POST('/api/pdf-files', {
      body: {
        sha256,
        creator: identifiedUser.identifier,
        fileName: file.name,
        bytesCount: file.size,
        pagesCount: document.value.numPages,
      },
    })
    assert(response.data !== undefined)
    const uploadUrl = response.data.uploadUrl
    if (uploadUrl !== null) {
      uploading.value = true
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      })
      assert(uploadResponse.status === 200)
      uploading.value = false
    }
    uploadedFileSha256.value = sha256
  }
}

async function submit() {
  assert(uploadedFileSha256.value !== null)
  const response = await client.POST('/api/extraction-batches', {
    body: {
      creator: identifiedUser.identifier,
      pdfFileSha256: uploadedFileSha256.value,
      firstPage: firstPageNumber.value,
      pagesCount: lastPageNumber.value - firstPageNumber.value + 1,
      strategy,
      runClassification: runClassification.value,
      modelForAdaptation: runAdaptation.value ? modelForAdaptation.value : null,
    },
  })
  if (response.data !== undefined) {
    router.push({ name: 'extraction-batch', params: { id: response.data.id } })
  }
}

const firstPage = computedAsync(async () => {
  if (document.value === null) {
    return null
  } else {
    return await document.value.getPage(firstPageNumber.value)
  }
}, null)

const lastPage = computedAsync(async () => {
  if (document.value === null) {
    return null
  } else {
    return await document.value.getPage(lastPageNumber.value)
  }
}, null)
</script>

<template>
  <ResizableColumns :columns="[1, 1]">
    <template #col-1>
      <p>Created by: <IdentifiedUser /></p>
      <h1>Strategy</h1>
      <h2>LLM model</h2>
      <p>
        <LlmModelSelector
          :availableLlmModels="apiConstantsStore.availableExtractionLlmModels"
          :disabled="false"
          v-model="strategy.model"
        />
      </p>
      <h2>Settings</h2>
      <AdaptedExerciseJsonSchemaDetails :schema="apiConstantsStore.extractionLlmResponseSchema" />
      <h3>Prompt</h3>
      <TextArea data-cy="prompt" v-model="strategy.prompt"></TextArea>
    </template>
    <template #col-2>
      <h1>Follow-ups</h1>
      <p>
        Run classification after extraction:
        <select data-cy="run-classification" v-model="runClassificationAsString">
          <option>yes</option>
          <option>no</option></select
        ><template v-if="runClassification">
          using <code>classification_camembert.pt</code>, provided by Elise by e-mail on 2025-05-20</template
        >
      </p>
      <p v-if="runClassification">
        Run adaptations after classification:
        <select data-cy="run-adaptation" v-model="runAdaptationAsString">
          <option>yes</option>
          <option>no</option>
        </select>
        <template v-if="runAdaptation">
          using
          <LlmModelSelector
            :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
            :disabled="false"
            v-model="modelForAdaptation"
          >
            <template #provider>provider</template>
            <template #model> and model</template>
          </LlmModelSelector>
          with the latest settings for each known exercise class.</template
        >
      </p>
      <h1>Input</h1>
      <p>
        PDF file: <input type="file" @change="openFile" accept=".pdf" :disabled="uploading" />
        <template v-if="uploading"> (uploading...)</template>
        <template v-if="uploadedFileSha256 !== null"> (uploaded)</template>
      </p>
      <template v-if="document !== null">
        <p>
          Pages: from
          <span class="pagePreview">
            <PdfNavigationControls v-model:page="firstPageNumber" :pagesCount="document.numPages" />
            <PdfPageRenderer v-if="firstPage !== null" :page="firstPage" />
          </span>
          to
          <span class="pagePreview">
            <PdfNavigationControls v-model:page="lastPageNumber" :pagesCount="document.numPages" />
            <PdfPageRenderer v-if="lastPage !== null" :page="lastPage" />
          </span>
          (of {{ document.numPages }})
        </p>
      </template>
      <p><button @click="submit" :disabled>Submit</button></p>
    </template>
  </ResizableColumns>
</template>

<style scoped>
.pagePreview {
  display: inline-block;
  vertical-align: top;
  width: 35%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.pagePreview > p {
  margin: 0;
}
</style>
