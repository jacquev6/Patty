<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient, type PostTextbookRequestBody } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import InputForNumberOrNull from '$/InputForNumberOrNull.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '@/reusable/WhiteSpace.vue'
import PdfRangeFormInputs from './PdfRangesFormInputs.vue'
import assert from '$/assert'

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

const singleOrMultiplePdfs = ref<'single' | 'multiple' | null>(null)

const uploadedFileSha256 = ref<string | null>(null)
const matchesExpectations = ref(false)
const pdfToTextbookPageNumbersDelta = ref(0)
const textbookPagesRangesToImport = ref<[number, number][]>([])
const modelForExtraction = ref(apiConstantsStore.availableExtractionLlmModels[0])
const modelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])

const disabled = computed(
  () =>
    title.value === '' ||
    singleOrMultiplePdfs.value === null ||
    (singleOrMultiplePdfs.value === 'single' && uploadedFileSha256.value === null),
)

async function submit() {
  const singlePdf: PostTextbookRequestBody['singlePdf'] =
    singleOrMultiplePdfs.value === 'single' && uploadedFileSha256.value !== null
      ? {
          pdfFileSha256: uploadedFileSha256.value,
          pdfToTextbookPageNumbersDelta: pdfToTextbookPageNumbersDelta.value,
          textbookPagesRanges: textbookPagesRangesToImport.value,
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
  assert(response.data !== undefined)
  router.push({ name: 'textbook', params: { id: response.data.id } })
}
</script>

<template>
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
    <PdfRangeFormInputs
      :expectedSha256="null"
      :pdfToTextbookPageNumbersFixedDelta="null"
      :knownPages="[]"
      v-model:sha256="uploadedFileSha256"
      v-model:matchesExpectations="matchesExpectations"
      v-model:pdfToTextbookPageNumbersDelta="pdfToTextbookPageNumbersDelta"
      v-model:textbookPagesRangesToImport="textbookPagesRangesToImport"
      v-model:modelForExtraction="modelForExtraction"
      v-model:modelForAdaptation="modelForAdaptation"
    >
      <template #openPdf>{{ t('open') }}</template>
    </PdfRangeFormInputs>
  </template>
  <p>
    <button @click="submit" :disabled>{{ t('submit') }}</button>
  </p>
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
