<script setup lang="ts">
import { computed, ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient, type PostTextbookRequestBody } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import BusyBox from '$/BusyBox.vue'
import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import InputForNumberOrNull from '$/InputForNumberOrNull.vue'
import { type PDFDocumentProxy } from '$/pdfjs'
import UploadPdfForm from '@/frontend/UploadPdfForm.vue'
import PdfPagesRangeSelector from '$/PdfPagesRangeSelector.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '@/reusable/WhiteSpace.vue'

const router = useRouter()
const { t } = useI18n()

const client = useAuthenticatedClient()
const apiConstantsStore = useApiConstantsStore()
const identifiedUser = useIdentifiedUserStore()

const title = ref('')
const publisher = ref<string | null>(null)
const year = ref<number | null>(null)
const isbn = ref<string | null>(null)
const pagesCount = ref<number | null>(null)

const busy = ref(false)

const singleOrMultiplePdfs = ref<'single' | 'multiple' | null>(null)

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

const disabled = computed(
  () =>
    title.value === '' ||
    singleOrMultiplePdfs.value === null ||
    (singleOrMultiplePdfs.value === 'single' && uploadedFileSha256.value === null),
)

async function submit() {
  busy.value = true

  const singlePdf: PostTextbookRequestBody['singlePdf'] =
    singleOrMultiplePdfs.value === 'single' && uploadedFileSha256.value !== null
      ? {
          pdfFileSha256: uploadedFileSha256.value,
          pdfFirstPageNumber: firstPdfPageNumber.value,
          textbookFirstPageNumber: firstTextbookPageNumber.value,
          pagesCount: lastPdfPageNumber.value - firstPdfPageNumber.value + 1,
          modelForExtraction: modelForExtraction.value,
          modelForAdaptation: modelForAdaptation.value,
        }
      : null

  const response = await client.POST('/api/textbooks', {
    body: {
      creator: identifiedUser.identifier,
      title: title.value,
      publisher: publisher.value,
      year: year.value,
      isbn: isbn.value,
      pagesCount: pagesCount.value,
      singlePdf,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'textbook', params: { id: response.data.id } })
  }
}
</script>

<template>
  <BusyBox :busy>
    <p>
      <label>{{ t('title') }} <input v-model="title" data-cy="textbook-title" /></label>
    </p>
    <p>
      <label>
        {{ t('publisher') }}
        <InputForNonEmptyStringOrNull v-model="publisher" data-cy="textbook-publisher" />
      </label>
    </p>
    <p>
      <label>{{ t('year') }} <InputForNumberOrNull v-model="year" data-cy="textbook-year" /></label>
    </p>
    <p>
      <label>{{ t('isbn') }} <InputForNonEmptyStringOrNull v-model="isbn" data-cy="textbook-isbn" /></label>
    </p>
    <p>
      <label>{{ t('pagesCount') }} <InputForNumberOrNull v-model="pagesCount" data-cy="textbook-pages-count" /></label>
    </p>
    <p>
      <label>
        {{ t('singlePdf.label') }}
        <input type="radio" v-model="singleOrMultiplePdfs" value="single" />
        <WhiteSpace />
        <span class="discrete">({{ t('singlePdf.description') }})</span>
      </label>
    </p>
    <p>
      <label>
        {{ t('multiplePdfs.label') }}
        <input type="radio" v-model="singleOrMultiplePdfs" value="multiple" />
        <WhiteSpace />
        <span class="discrete">({{ t('multiplePdfs.description') }})</span>
      </label>
    </p>
    <template v-if="singleOrMultiplePdfs === 'single'">
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
    </template>
    <p>
      <button @click="submit" :disabled>{{ t('submit') }}</button>
    </p>
  </BusyBox>
</template>

<style scoped>
.discrete {
  color: gray;
  font-size: 90%;
}
</style>

<i18n>
en:
  createdBy: Created by
  title: "Title:"
  publisher: "Publisher:"
  year: "Year:"
  isbn: "ISBN:"
  pagesCount: "Pages count:"
  singlePdf:
    label: Single PDF
    description: When you have a single PDF file containing the whole textbook. You will only be able to upload one PDF for this textbook, now.
  multiplePdfs:
    label: Multiple PDFs
    description: When the textbook is split into several PDF files. You will be able to upload multiple PDFs for this textbook later.
  open: "Open the PDF file containing the textbook:"
  modelForExtraction: "Model provider for extraction:"
  modelForAdaptation: "Model provider for adaptation:"
  submit: Submit
fr:
  createdBy: "Créé par"
  title: "Titre :"
  publisher: "Éditeur :"
  year: "Année :"
  isbn: "ISBN :"
  pagesCount: "Nombre de pages :"
  singlePdf:
    label: PDF unique
    description: Lorsque vous avez un seul fichier PDF contenant l'ensemble du manuel. Vous ne pourrez téléverser qu'un seul PDF pour ce manuel, maintenant.
  multiplePdfs:
    label: PDF multiples
    description: Lorsque le manuel est divisé en plusieurs fichiers PDF. Vous pourrez téléverser plusieurs PDF pour ce manuel plus tard.
  open: "Ouvrir le fichier PDF contenant le manuel :"
  modelForExtraction: "Fournisseur de modèle pour l'extraction :"
  modelForAdaptation: "Fournisseur de modèle pour l'adaptation :"
  submit: Soumettre
</i18n>
