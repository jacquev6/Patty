<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import PdfRangeFormInputs from './PdfRangesFormInputs.vue'

const props = defineProps<{
  textbook: Textbook
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()
const identifiedUser = useIdentifiedUserStore()
const apiConstantsStore = useApiConstantsStore()
const router = useRouter()

const uploadedFileSha256 = ref<string | null>(null)
const matchesExpectations = ref(false)
const pdfToTextbookPageNumbersDelta = ref(0)
const textbookPagesRangesToImport = ref<[number, number][]>([])
const modelForExtraction = ref(apiConstantsStore.availableExtractionLlmModels[0])
const modelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])

const disabled = computed(
  () =>
    uploadedFileSha256.value === null || !matchesExpectations.value || textbookPagesRangesToImport.value.length === 0,
)

const busy = ref(false)
const rangeInputs = useTemplateRef('rangeInputs')

const pdfToTextbookPageNumbersFixedDelta = computed(() => {
  if (props.textbook.singlePdf !== null) {
    return props.textbook.singlePdf.pdfToTextbookPageNumbersDelta
  } else if (uploadedFileSha256.value !== null && uploadedFileSha256.value in props.textbook.knownPdfs) {
    return props.textbook.knownPdfs[uploadedFileSha256.value].pdfToTextbookPageNumbersDelta
  } else {
    return null
  }
})

const knownPages = computed(() => {
  if (uploadedFileSha256.value === null || !(uploadedFileSha256.value in props.textbook.knownPdfs)) {
    return []
  } else {
    return props.textbook.knownPdfs[uploadedFileSha256.value].extractedTextbookPages
  }
})

async function submit() {
  busy.value = true

  assert(uploadedFileSha256.value !== null)

  const response = await client.POST('/api/textbooks/{id}/ranges', {
    params: { path: { id: props.textbook.id } },
    body: {
      creator: identifiedUser.identifier,
      pdfFileSha256: uploadedFileSha256.value,
      pdfToTextbookPageNumbersDelta: pdfToTextbookPageNumbersDelta.value,
      textbookPagesRanges: textbookPagesRangesToImport.value,
      modelForExtraction: modelForExtraction.value,
      modelForAdaptation: modelForAdaptation.value,
    },
  })
  assert(response.response.status === 200)

  router.push({
    name: 'textbook-page',
    params: { textbookId: props.textbook.id, pageNumber: textbookPagesRangesToImport.value[0][0] },
  })
  busy.value = false
  assert(rangeInputs.value !== null)
  rangeInputs.value.reset()
}
</script>

<template>
  <PdfRangeFormInputs
    ref="rangeInputs"
    :expectedSha256="textbook.singlePdf === null ? null : textbook.singlePdf.sha256"
    :pdfToTextbookPageNumbersFixedDelta
    :knownPages
    v-model:matchesExpectations="matchesExpectations"
    v-model:sha256="uploadedFileSha256"
    v-model:pdfToTextbookPageNumbersDelta="pdfToTextbookPageNumbersDelta"
    v-model:textbookPagesRangesToImport="textbookPagesRangesToImport"
    v-model:modelForExtraction="modelForExtraction"
    v-model:modelForAdaptation="modelForAdaptation"
  >
    <template #openPdf>
      <template v-if="textbook.singlePdf === null">
        {{ t('openAPdf') }}
      </template>
      <template v-else>
        <i18n-t keypath="openThePdf">
          <template #names>
            <template v-for="(name, index) in textbook.singlePdf.knownNames">
              <template v-if="index > 0">, </template>
              <code>{{ name }}</code>
            </template>
          </template>
        </i18n-t>
      </template>
    </template>
    <template #pdfUploaded>
      <button @click="submit" :disabled>{{ t('submit') }}</button>
    </template>
  </PdfRangeFormInputs>
</template>

<i18n>
en:
  openThePdf: "Open the PDF file containing the textbook ({names}):"
  openAPdf: "Open a PDF file containing the textbook (or a part of it):"
  submit: "Submit"
fr:
  openThePdf: "Ouvrir le fichier PDF contenant le manuel ({names}) :"
  openAPdf: "Ouvrir un fichier PDF contenant le manuel (ou une partie de celui-ci) :"
  submit: "Soumettre"
</i18n>
