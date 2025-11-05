<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import shajs from 'sha.js'
import { useI18n } from 'vue-i18n'

import pdfjs, { type PDFDocumentProxy } from '$/pdfjs'
import assert from '$/assert'
import { useAuthenticatedClient } from './ApiClient'
import { useIdentifiedUserStore } from './basic/IdentifiedUserStore'

const props = defineProps<{
  expectedSha256: string | null
  showUploaded: boolean
}>()

const emit = defineEmits<{
  // @todo Accept models instead of emiting events?
  (e: 'file-selected'): void
  (e: 'document-opened', document: PDFDocumentProxy, matchesExpectations: boolean): void
  (e: 'file-uploaded', sha256: string): void
}>()

const client = useAuthenticatedClient()
const identifiedUser = useIdentifiedUserStore()
const { t } = useI18n()

const uploading = ref(false)
const uploaded = ref(false)

async function openFile(event: Event) {
  uploaded.value = false
  emit('file-selected')

  const input = event.target as HTMLInputElement
  assert(input.files !== null)
  if (input.files.length == 1) {
    uploading.value = true
    const file = input.files[0]
    const data = await file.arrayBuffer()

    const startTime = performance.now()
    const documentTask = pdfjs.getDocument({ data })
    const sha256 = shajs('sha256').update(new Uint8Array(data)).digest('hex')
    console.info(`Computed sha256 for ${file.name} in ${Math.round(performance.now() - startTime)}ms: ${sha256}`)
    // We could use documentTask.onProgress to report progress to the user
    const document = await documentTask.promise
    console.info(`Loaded ${file.name} in ${Math.round(performance.now() - startTime)}ms`)
    const matchesExpectations = props.expectedSha256 === null || sha256 === props.expectedSha256
    emit('document-opened', document, matchesExpectations)

    if (matchesExpectations) {
      const response = await client.POST('/api/pdf-files', {
        body: {
          sha256,
          creator: identifiedUser.identifier,
          fileName: file.name,
          bytesCount: file.size,
          pagesCount: document.numPages,
        },
      })
      assert(response.data !== undefined)
      const uploadUrl = response.data.uploadUrl
      if (uploadUrl !== null) {
        const uploadResponse = await fetch(uploadUrl, {
          method: 'PUT',
          headers: { 'Content-Type': file.type },
          body: file,
        })
        assert(uploadResponse.status === 200)
      }
    }
    uploading.value = false
    uploaded.value = true
    emit('file-uploaded', sha256)
  }
}

const input = useTemplateRef('input')

defineExpose({
  reset() {
    assert(input.value !== null)
    input.value.value = ''
    emit('file-selected')
  },
})
</script>

<template>
  <span>
    <input ref="input" type="file" lang="fr" @change="openFile" accept=".pdf" :disabled="uploading" />
    <template v-if="uploading"> ({{ t('uploading') }})</template>
    <template v-if="uploaded && showUploaded"> ({{ t('uploaded') }})</template>
  </span>
</template>

<i18n>
en:
  uploading: "uploading..."
  uploaded: "uploaded"
fr:
  uploading: "import en cours..."
  uploaded: "importé"
</i18n>
