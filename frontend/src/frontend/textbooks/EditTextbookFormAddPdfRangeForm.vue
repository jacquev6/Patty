<script setup lang="ts">
import { computed, ref, shallowRef, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'

import { type PDFDocumentProxy } from '$/pdfjs'
import UploadPdfForm from '@/frontend/UploadPdfForm.vue'
import PdfPagesRangeSelector from '$/PdfPagesRangeSelector.vue'
import { useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'

const props = defineProps<{
  textbookId: string
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
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

  const response = await client.POST('/api/textbooks/{id}/ranges', {
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

  emit('textbook-updated')
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
      <template #provider>{{ t('modelForExtraction') }}</template>
    </LlmModelSelector>
  </p>
  <p data-cy="adaptation">
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
      :disabled="false"
      v-model="modelForAdaptation"
    >
      <template #provider>{{ t('modelForAdaptation') }}</template>
    </LlmModelSelector>
  </p>
  <p>
    <button @click="submit" :disabled>{{ t('submit') }}</button>
  </p>
</template>

<i18n>
en:
  open: "Open a PDF file containing the textbook (or a part of it):"
  modelForExtraction: "Model provider for extraction:"
  modelForAdaptation: "Model provider for adaptation:"
  submit: "Submit"
fr:
  open: "Ouvrir un fichier PDF contenant le manuel (ou une partie de celui-ci) :"
  modelForExtraction: "Fournisseur de modèle pour l'extraction :"
  modelForAdaptation: "Fournisseur de modèle pour l'adaptation :"
  submit: "Soumettre"
</i18n>
