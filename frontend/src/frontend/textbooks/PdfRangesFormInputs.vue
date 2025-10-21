<script lang="ts">
import assert from '$/assert'

type PagesGroup = {
  first: number
  last: number
  excluded: number[]
}

export function makePagesGroups(
  firstPage: number,
  lastPage: number,
  excludedPages: number[],
  groupSize: number = 5,
): PagesGroup[] {
  const groups: PagesGroup[] = []
  const firstFirst = 1 + Math.floor((firstPage - 1) / groupSize) * groupSize
  for (let maybeFirst = firstFirst; maybeFirst <= lastPage; maybeFirst += groupSize) {
    const first = Math.max(1, maybeFirst, firstPage)
    const last = Math.min(maybeFirst + groupSize - 1, lastPage)
    groups.push({ first, last, excluded: [] })
  }
  for (const excludedPage of [...new Set(excludedPages)].sort((a, b) => a - b)) {
    const groupIndex = Math.floor((excludedPage - firstFirst) / groupSize)
    groups[groupIndex].excluded.push(excludedPage)
  }
  return groups.filter((group) => group.excluded.length < group.last - group.first + 1)
}

export function mergePagesGroups(groups: PagesGroup[]): [number, number][] {
  const sortedPages = []
  for (const group of groups) {
    for (let i = group.first; i <= group.last; i++) {
      if (!group.excluded.includes(i)) {
        sortedPages.push(i)
      }
    }
  }
  if (sortedPages.length === 0) {
    return []
  } else {
    const ranges: [number, number][] = [[sortedPages[0], sortedPages[0]]]
    for (const page of sortedPages.slice(1)) {
      if (page === ranges[ranges.length - 1][1] + 1) {
        ranges[ranges.length - 1][1] = page
      } else {
        assert(page > ranges[ranges.length - 1][1] + 1)
        ranges.push([page, page])
      }
    }
    return ranges
  }
}
</script>

<script setup lang="ts">
import { computed, ref, shallowRef, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { type PDFDocumentProxy } from '$/pdfjs'
import UploadPdfForm from '@/frontend/UploadPdfForm.vue'
import PdfToTextbookPagesDeltaEditor from '@/frontend/textbooks/PdfToTextbookPagesDeltaEditor.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '$/WhiteSpace.vue'
import { type ExtractionLlmModel, type AdaptationLlmModel } from '@/frontend/ApiClient'
import FixedColumns from '$/FixedColumns.vue'
import ThreeStatesCheckbox from '$/ThreeStatesCheckbox.vue'

const props = defineProps<{
  expectedSha256: string | null
  pdfToTextbookPageNumbersFixedDelta: number | null
  knownPages: number[]
}>()

const uploadedFileSha256 = defineModel<string | null>('sha256', { required: true })
const matchesExpectations = defineModel<boolean>('matchesExpectations', { required: true })
const pdfToTextbookPageNumbersDelta = defineModel<number>('pdfToTextbookPageNumbersDelta', { required: true })
const rangesModel = defineModel<[number, number][]>('textbookPagesRangesToImport', { required: true })
const modelForExtraction = defineModel<ExtractionLlmModel>('modelForExtraction', { required: true })
const modelForAdaptation = defineModel<AdaptationLlmModel>('modelForAdaptation', { required: true })

const { t } = useI18n()
const apiConstantsStore = useApiConstantsStore()

const document = shallowRef<PDFDocumentProxy | null>(null)
const previewedPdfPageNumber = ref(0)
const previewedTextbookPageNumber = ref(0)

watch([previewedPdfPageNumber, previewedTextbookPageNumber], ([pdfPage, textbookPage]) => {
  pdfToTextbookPageNumbersDelta.value = textbookPage - pdfPage
})

function fileSelected() {
  uploadedFileSha256.value = null
  document.value = null
  previewedPdfPageNumber.value = 1
  previewedTextbookPageNumber.value = 1 + (props.pdfToTextbookPageNumbersFixedDelta ?? 0)
}

function documentOpened(doc: PDFDocumentProxy, matches: boolean) {
  document.value = doc
  matchesExpectations.value = matches
  previewedPdfPageNumber.value = 1
  previewedTextbookPageNumber.value = 1 + (props.pdfToTextbookPageNumbersFixedDelta ?? 0)
}

watch(
  () => props.pdfToTextbookPageNumbersFixedDelta,
  (newDelta) => {
    if (newDelta !== null) {
      previewedTextbookPageNumber.value = previewedPdfPageNumber.value + newDelta
    }
  },
)

function fileUploaded(sha256: string) {
  uploadedFileSha256.value = sha256
}

const uploadForm = useTemplateRef('uploadForm')

const pageGroups = computed(() => {
  if (document.value === null) {
    return []
  } else {
    const delta = props.pdfToTextbookPageNumbersFixedDelta ?? pdfToTextbookPageNumbersDelta.value
    return makePagesGroups(Math.max(1, 1 + delta), document.value.numPages + delta, props.knownPages)
  }
})

const groupsToImport = ref<Set<number>>(new Set())

watch(
  groupsToImport,
  (groupIndexes) => {
    const groups = pageGroups.value.filter((_, index) => groupIndexes.has(index))
    rangesModel.value = mergePagesGroups(groups)
  },
  { immediate: true, deep: true },
)

const importAllGroups = computed({
  get: () => {
    if (groupsToImport.value.size === pageGroups.value.length) {
      return true
    } else if (groupsToImport.value.size === 0) {
      return false
    } else {
      return null
    }
  },
  set: (value: boolean | null) => {
    if (value === true) {
      groupsToImport.value = new Set(pageGroups.value.map((_, index) => index))
    } else if (value === false) {
      groupsToImport.value = new Set()
    } else {
      // Nothing to do
    }
  },
})

defineExpose({
  reset: () => {
    uploadForm.value?.reset()
  },
})
</script>

<template>
  <p>
    <slot name="openPdf"></slot>
    <WhiteSpace />
    <UploadPdfForm
      ref="uploadForm"
      :expectedSha256
      @fileSelected="fileSelected"
      @documentOpened="documentOpened"
      @fileUploaded="fileUploaded"
    />
  </p>
  <template v-if="document !== null && matchesExpectations">
    <FixedColumns :columns="[1, 1]">
      <template #col-1>
        <PdfToTextbookPagesDeltaEditor
          :pdfToTextbookPageNumbersFixedDelta
          v-model:pdfPageNumber="previewedPdfPageNumber"
          v-model:textbookPageNumber="previewedTextbookPageNumber"
          :document="document"
        >
          <template #label>{{ t('pagesMapping') }} </template>
        </PdfToTextbookPagesDeltaEditor>
      </template>
      <template #col-2>
        <h3>{{ t('textbookPagesToImport') }}</h3>
        <p v-if="pageGroups.length === 0">{{ t('noneAllImported') }}</p>
        <template v-else>
          <p>
            <label><ThreeStatesCheckbox v-model="importAllGroups" /><WhiteSpace />{{ t('allPages') }}</label>
          </p>
          <p v-for="(group, groupIndex) in pageGroups">
            <label>
              <input type="checkbox" v-model="groupsToImport" :value="groupIndex" />
              <WhiteSpace />
              <strong>{{ group.first }}-{{ group.last }}</strong>
              <template v-if="group.excluded.length !== 0">
                ({{ t('except') }}
                <template v-for="(page, index) in group.excluded">
                  <template v-if="index > 0">, </template>{{ page }} </template
                >)
              </template>
            </label>
          </p>
        </template>
      </template>
    </FixedColumns>
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
  <p v-else-if="document !== null && !matchesExpectations" class="error">
    {{ t('theSha256OfTheSelectedFileDoesNotMatchTheExpectedOne') }}
  </p>
</template>

<i18n>
en:
  pagesMapping: "Pages mapping:"
  textbookPagesToImport: Textbook pages to import
  allPages: All pages
  except: except
  noneAllImported: "None (all imported)"
  modelForExtraction: "Model provider for extraction:"
  modelForAdaptation: "Model provider for adaptation:"
  theSha256OfTheSelectedFileDoesNotMatchTheExpectedOne: This is not the PDF used to create this textbook. Patty can only work with the exact original file.
fr:
  pagesMapping: "Correspondance des pages :"
  textbookPagesToImport: Pages du manuel à importer
  allPages: Toutes les pages
  except: sauf
  noneAllImported: "Aucune (toutes importées)"
  modelForExtraction: "Fournisseur de modèle pour l'extraction :"
  modelForAdaptation: "Fournisseur de modèle pour l'adaptation :"
  theSha256OfTheSelectedFileDoesNotMatchTheExpectedOne: Ceci n'est pas le PDF utilisé pour créer ce manuel. Patty ne peut fonctionner qu'avec le fichier original exact.
</i18n>
