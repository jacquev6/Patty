<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { computed, reactive, ref, shallowRef, watch } from 'vue'
import { useRouter } from 'vue-router'
import { computedAsync } from '@vueuse/core'
import deepCopy from 'deep-copy'
import { useI18n } from 'vue-i18n'

import { type PDFDocumentProxy } from '$/pdfjs'
import { type ExtractionStrategy, useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import assert from '$/assert'
import PdfPageRenderer from '$/PdfPageRenderer.vue'
import PdfNavigationControls from '$/PdfNavigationControls.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import ResizableColumns from '$/ResizableColumns.vue'
import AdaptedExerciseJsonSchemaDetails from '@/frontend/common/AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from '$/TextArea.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '$/WhiteSpace.vue'
import UploadPdfForm from '@/frontend/UploadPdfForm.vue'

const props = defineProps<{
  latestExtractionStrategy: ExtractionStrategy
}>()

const router = useRouter()
const { t } = useI18n()

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
watch(
  () => strategy.outputSchemaVersion,
  async () => {
    const response = await client.GET('/api/latest-extraction-strategy', {
      params: { query: { version: strategy.outputSchemaVersion } },
    })
    if (response.data !== undefined) {
      Object.assign(strategy, deepCopy(response.data))
    }
  },
)

const schema = computedAsync(async () => {
  const response = await client.GET('/api/extraction-llm-response-schema', {
    params: { query: { version: strategy.outputSchemaVersion } },
  })
  assert(response.data !== undefined)
  return response.data
}, {})

const runClassificationAsString = ref<'yes' | 'no'>('yes')
const runClassification = computed(() => runClassificationAsString.value === 'yes')

const runAdaptationAsString = ref<'yes' | 'no'>('no')
const modelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])
const runAdaptation = computed(() => runClassification.value && runAdaptationAsString.value === 'yes')

const uploadedFileSha256 = ref<string | null>(null)
const document = shallowRef<PDFDocumentProxy | null>(null)
const firstPageNumber = ref(1)
const lastPageNumber = ref(1)

function fileSelected() {
  uploadedFileSha256.value = null
  document.value = null
  firstPageNumber.value = 1
  lastPageNumber.value = 1
}

function documentOpened(doc: PDFDocumentProxy) {
  document.value = doc
  firstPageNumber.value = 1
  lastPageNumber.value = doc.numPages
}

function fileUploaded(sha256: string) {
  uploadedFileSha256.value = sha256
}

const disabled = computed(
  () =>
    uploadedFileSha256.value === null ||
    firstPageNumber.value < 1 ||
    lastPageNumber.value < firstPageNumber.value ||
    lastPageNumber.value > (document.value?.numPages ?? 0),
)

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

const columns = [
  { name: 'col-1', width: 1 },
  { name: 'col-2', width: 1 },
]
</script>

<template>
  <ResizableColumns :columns>
    <template #col-1>
      <h1>{{ t('strategy') }}</h1>
      <h2>{{ t('llmModel') }}</h2>
      <p>
        <LlmModelSelector
          :availableLlmModels="apiConstantsStore.availableExtractionLlmModels"
          :disabled="false"
          v-model="strategy.model"
        />
      </p>
      <h2>{{ t('settings') }}</h2>
      <p>
        <label>
          {{ t('outputSchemaVersion') }}
          <select v-model="strategy.outputSchemaVersion">
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <option value="v2">v2</option>
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <option value="v3">v3</option>
          </select>
        </label>
        {{ t(`outputSchemaVersionDescriptions.${strategy.outputSchemaVersion}`) }}
      </p>
      <AdaptedExerciseJsonSchemaDetails :schema />
      <h3>{{ t('prompt') }}</h3>
      <TextArea data-cy="prompt" v-model="strategy.prompt"></TextArea>
    </template>
    <template #col-2>
      <h1>{{ t('followUps') }}</h1>
      <p>
        {{ t('runClassification') }}
        <select data-cy="run-classification" v-model="runClassificationAsString">
          <option value="yes">{{ t('yes') }}</option>
          <option value="no">{{ t('no') }}</option>
        </select>
      </p>
      <p v-if="runClassification">
        {{ t('runAdaptation') }}
        <select data-cy="run-adaptation" v-model="runAdaptationAsString">
          <option value="yes">{{ t('yes') }}</option>
          <option value="no">{{ t('no') }}</option>
        </select>
        <template v-if="runAdaptation">
          <WhiteSpace />
          <I18nT keypath="runAdaptationUsing">
            <LlmModelSelector
              :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
              :disabled="false"
              v-model="modelForAdaptation"
            >
              <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
              <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
            </LlmModelSelector>
          </I18nT>
        </template>
      </p>
      <h1>{{ t('input') }}</h1>
      <p>
        {{ t('pdfFile') }}
        <UploadPdfForm
          :expectedSha256="null"
          :showUploaded="true"
          @fileSelected="fileSelected"
          @documentOpened="documentOpened"
          @fileUploaded="fileUploaded"
        />
      </p>
      <template v-if="document !== null">
        <I18nT keypath="pages" tag="p">
          <template #from>
            <span class="pagePreview">
              <PdfNavigationControls v-model="firstPageNumber" :pagesCount="document.numPages" />
              <PdfPageRenderer v-if="firstPage !== null" :page="firstPage" />
            </span>
          </template>
          <template #to>
            <span class="pagePreview">
              <PdfNavigationControls v-model="lastPageNumber" :pagesCount="document.numPages" />
              <PdfPageRenderer v-if="lastPage !== null" :page="lastPage" />
            </span>
          </template>
          <template #count>{{ document.numPages }}</template>
        </I18nT>
      </template>
      <p>
        <button @click="submit" :disabled>{{ t('submit') }}</button>
      </p>
    </template>
  </ResizableColumns>
</template>

<i18n>
en:
  strategy: Strategy
  llmModel: LLM model
  settings: Settings
  outputSchemaVersion: "Output schema:"
  outputSchemaVersionDescriptions:
    v2: "fields in French (e.g. 'consignes', 'autre'), text and styles ignored"
    v3: "fields in English (e.g. 'instruction', 'labels'), text and styles extracted and added to prompt"
  prompt: Prompt
  followUps: Follow-ups
  runClassification: "Run classification after extraction:"
  runAdaptation: "Run adaptations after classification:"
  runAdaptationUsing: "using {0} with the latest settings for each known exercise class."
  runAdaptationUsingProvider: "provider"
  runAdaptationUsingModel: "and model"
  yes: yes
  no: no
  input: Input
  pdfFile: "PDF file:"
  uploading: "uploading..."
  uploaded: "uploaded"
  pages: "Pages: from {from} to {to} (of {count})"
  submit: Submit
fr:
  strategy: Stratégie
  llmModel: Modèle LLM
  settings: Paramètres
  prompt: Invite
  outputSchemaVersion: "Schéma de sortie :"
  outputSchemaVersionDescriptions:
    v2: "champs en français (e.g. 'consignes', 'autre'), texte et styles ignorés"
    v3: "champs en anglais (e.g. 'instruction', 'labels'), texte et styles extraits et ajoutés à l'invite"
  followUps: Étapes suivantes
  runClassification: "Exécuter la classification après l'extraction :"
  runAdaptation: "Exécuter les adaptations après la classification :"
  runAdaptationUsing: "avec {0} avec les derniers paramètres pour chaque classe d'exercice connue."
  runAdaptationUsingProvider: "fournisseur"
  runAdaptationUsingModel: "et modèle"
  yes: oui
  no: non
  input: Entrée
  pdfFile: "Fichier PDF :"
  uploading: "import en cours..."
  uploaded: "importé"
  pages: "Pages : de {from} à {to} (sur {count})"
  submit: Envoyer
</i18n>

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
