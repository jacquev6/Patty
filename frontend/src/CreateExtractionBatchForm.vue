<script setup lang="ts">
import { computed, ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import shajs from 'sha.js'
import { computedAsync } from '@vueuse/core'

import pdfjs, { type PDFDocumentProxy } from './pdfjs'
import { type AdaptationLlmModel, useAuthenticatedClient } from './apiClient'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import assert from './assert'
import PdfPageRenderer from './PdfPageRenderer.vue'
import PdfNavigationControls from './PdfNavigationControls.vue'

defineProps<{
  availableAdaptationLlmModels: AdaptationLlmModel[]
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

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
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
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
