<script setup lang="ts">
import { computed, ref, shallowRef, useTemplateRef } from 'vue'
import { type PDFDocumentProxy } from './pdfjs'
import { useI18n } from 'vue-i18n'

import { type Textbook } from './apiClient'
import UploadPdfForm from './UploadPdfForm.vue'
import PdfPagesRangeSelector from './PdfPagesRangeSelector.vue'
import { useAuthenticatedClient } from './apiClient'
import assert from './assert'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import LlmModelSelector from './LlmModelSelector.vue'
import { useApiConstantsStore } from './ApiConstantsStore'

const props = defineProps<{
  textbookId: string
}>()

const emit = defineEmits<{
  (e: 'textbook-updated', textbook: Textbook): void
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()
const identifiedUser = useIdentifiedUserStore()
const apiConstantsStore = useApiConstantsStore()

const uploadedFileSha256 = ref<string | null>(null)
const document = shallowRef<PDFDocumentProxy | null>(null)
const firstPdfPageNumber = ref(1)
const lastPdfPageNumber = ref(1)
const firstTextbookPageNumber = ref(1)

function fileSelected() {
  uploadedFileSha256.value = null
  document.value = null
  firstPdfPageNumber.value = 1
  lastPdfPageNumber.value = 1
  firstTextbookPageNumber.value = 1
}

function documentOpened(doc: PDFDocumentProxy) {
  document.value = doc
  firstPdfPageNumber.value = 1
  lastPdfPageNumber.value = doc.numPages
  firstTextbookPageNumber.value = 1
}

function fileUploaded(sha256: string) {
  uploadedFileSha256.value = sha256
}

const modelForExtraction = ref(apiConstantsStore.availableExtractionLlmModels[0])
const modelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])

const disabled = computed(() => uploadedFileSha256.value === null)

const busy = ref(false)
const uploadForm = useTemplateRef('uploadForm')

async function submit() {
  busy.value = true

  assert(uploadedFileSha256.value !== null)

  const response = await client.POST('/api/textbooks/{id}/range', {
    params: { path: { id: props.textbookId } },
    body: {
      creator: identifiedUser.identifier,
      pdfFileSha256: uploadedFileSha256.value,
      pdfFirstPageNumber: firstPdfPageNumber.value,
      textbookFirstPageNumber: firstTextbookPageNumber.value,
      pagesCount: lastPdfPageNumber.value - firstPdfPageNumber.value + 1,
      modelForExtraction: modelForExtraction.value,
      modelForAdaptation: modelForAdaptation.value,
    },
  })
  assert(response.response.status === 200)

  const textbookResponse = await client.GET(`/api/textbooks/{id}`, {
    params: { path: { id: props.textbookId } },
  })
  assert(textbookResponse.data !== undefined)
  emit('textbook-updated', textbookResponse.data.textbook)
  busy.value = false
  assert(uploadForm.value !== null)
  uploadForm.value.reset()
}
</script>

<template>
  <p>
    {{ t('open') }}
    <UploadPdfForm
      ref="uploadForm"
      @fileSelected="fileSelected"
      @documentOpened="documentOpened"
      @fileUploaded="fileUploaded"
    />
  </p>
  <PdfPagesRangeSelector
    v-if="document !== null"
    v-model:firstInPdf="firstPdfPageNumber"
    v-model:lastInPdf="lastPdfPageNumber"
    v-model:firstInTextbook="firstTextbookPageNumber"
    :document="document"
  />
  <p data-cy="extraction">
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableExtractionLlmModels"
      :disabled="false"
      v-model="modelForExtraction"
    >
      <template #provider>Model provider for extraction:</template>
    </LlmModelSelector>
  </p>
  <p data-cy="adaptation">
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
      :disabled="false"
      v-model="modelForAdaptation"
    >
      <template #provider>Model provider for adaptation:</template>
    </LlmModelSelector>
  </p>
  <p>
    <button @click="submit" :disabled>{{ t('submit') }}</button>
  </p>
</template>

<i18n>
en:
  open: "Open a PDF file containing the textbook (or a part of it):"
  submit: "Submit"
fr:
  open: "Ouvrir un fichier PDF contenant le manuel (ou une partie de celui-ci) :"
  submit: "Soumettre"
</i18n>
