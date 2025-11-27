<script setup lang="ts">
import jsonStringifyPrettyCompact from 'json-stringify-pretty-compact'
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

import { useAuthenticatedClient, type ExtractionBatch } from '@/frontend/ApiClient'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import WhiteSpace from '$/WhiteSpace.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import ResizableColumns from '$/ResizableColumns.vue'
import AdaptedExerciseJsonSchemaDetails from '@/frontend/common/AdaptedExerciseJsonSchemaDetails.vue'
import MarkDown from '$/MarkDown.vue'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import classificationCamembert20250520 from '@/frontend/sandbox/ClassificationCamembert20250520'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'

const props = defineProps<{
  extractionBatch: ExtractionBatch
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const { t } = useI18n()
const { d } = useI18n({ useScope: 'global' })
const apiConstantsStore = useApiConstantsStore()
const client = useAuthenticatedClient()

const authenticationTokenStore = useAuthenticationTokenStore()

const editingRunClassification = ref(false)
async function submitClassification() {
  editingRunClassification.value = false
  await client.PUT('/api/extraction-batches/{id}/run-classification', {
    params: { path: { id: props.extractionBatch.id } },
  })
  emit('batch-updated')
}

const editingModelForAdaptation = ref(false)
const llmModelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])
async function submitAdaptation() {
  editingModelForAdaptation.value = false
  await client.PUT('/api/extraction-batches/{id}/model-for-adaptation', {
    params: { path: { id: props.extractionBatch.id } },
    body: llmModelForAdaptation.value,
  })
  emit('batch-updated')
}

async function submitAdaptationsWithRecentSettings() {
  await client.POST(`/api/extraction-batches/{id}/submit-adaptations-with-recent-settings`, {
    params: { path: { id: props.extractionBatch.id } },
  })
  emit('batch-updated')
}

const columns = [
  { name: 'col-1', width: 1 },
  { name: 'col-2', width: 2 },
]

function showDuration(timing: { start: number; end: number | null } | null): string {
  if (timing === null || timing.end === null) {
    return 'N/A'
  } else {
    const duration = timing.end - timing.start
    return `${duration.toFixed(1)}s`
  }
}
</script>

<template>
  <ResizableColumns :columns>
    <template #col-1>
      <p>{{ t('createdBy') }} {{ extractionBatch.createdBy }}</p>
      <h1>{{ t('strategy') }}</h1>
      <h2>{{ t('llmModel') }}</h2>
      <p><LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="extractionBatch.strategy.model" /></p>
      <h2>{{ t('settings') }}</h2>
      <AdaptedExerciseJsonSchemaDetails :schema="apiConstantsStore.extractionLlmResponseSchema" />
      <h3>{{ t('prompt') }}</h3>
      <MarkDown :markdown="extractionBatch.strategy.prompt" />
    </template>
    <template #col-2>
      <p>
        <I18nT keypath="download">
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}.html?token=${authenticationTokenStore.token}`"
          >
            {{ t('standaloneHtml') }}
          </a>
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}-extracted-exercises.json?token=${authenticationTokenStore.token}`"
          >
            {{ t('jsonDataForExtractedExercises') }}
          </a>
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}-extracted-exercises.tsv?token=${authenticationTokenStore.token}`"
          >
            {{ t('tsvDataForExtractedExercises') }}
          </a>
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}-classified-exercises.tsv?token=${authenticationTokenStore.token}`"
          >
            {{ t('tsvDataForClassifiedExercises') }}
          </a>
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}-adapted-exercises.json?token=${authenticationTokenStore.token}`"
          >
            {{ t('jsonDataForAdaptedExercises') }}
          </a>
          <a
            :href="`/api/export/sandbox-extraction-batch-${extractionBatch.id}-adapted-exercises.zip?token=${authenticationTokenStore.token}`"
          >
            {{ t('zipDataForAdaptedExercises') }}
          </a>
        </I18nT>
      </p>
      <h1>{{ t('followUps') }}</h1>
      <p>
        {{ t('runClassification') }}
        <template v-if="extractionBatch.runClassification">
          <I18nT keypath="runClassificationYesUsing">
            <code>{{ classificationCamembert20250520.fileName }}</code>
            <span>{{ classificationCamembert20250520.providedBy }}</span>
            <span>{{ d(classificationCamembert20250520.providedOn, 'long-date') }}</span>
          </I18nT>
        </template>
        <template v-else>
          <template v-if="editingRunClassification">
            <I18nT keypath="runClassificationYesUsing">
              <code>{{ classificationCamembert20250520.fileName }}</code>
              <span>{{ classificationCamembert20250520.providedBy }}</span>
              <span>{{ d(classificationCamembert20250520.providedOn, 'long-date') }}</span> </I18nT
            >: <button @click="submitClassification">{{ t('submit') }}</button>
          </template>
          <template v-else>
            {{ t('no') }}
            <span style="cursor: pointer" @click="editingRunClassification = true">({{ t('change') }})</span>
          </template>
        </template>
      </p>
      <p v-if="extractionBatch.runClassification">
        {{ t('runAdaptation') }}
        <template v-if="extractionBatch.modelForAdaptation === null">
          <template v-if="editingModelForAdaptation">
            <I18nT keypath="runAdaptationYesUsing">
              <LlmModelSelector
                :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
                :disabled="false"
                :modelValue="llmModelForAdaptation"
              >
                <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
                <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
              </LlmModelSelector> </I18nT
            >: <button @click="submitAdaptation">{{ t('submit') }}</button>
          </template>
          <template v-else>
            {{ t('no') }}
            <span style="cursor: pointer" @click="editingModelForAdaptation = true">({{ t('change') }})</span>
          </template>
        </template>
        <template v-else>
          <I18nT keypath="runAdaptationYesUsing">
            <LlmModelSelector
              :availableLlmModels="[]"
              :disabled="true"
              :modelValue="extractionBatch.modelForAdaptation"
            >
              <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
              <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
            </LlmModelSelector> </I18nT
          >.
        </template>
      </p>
      <h1>{{ t('result') }}</h1>
      <details>
        <summary>{{ t('timing.summary') }}</summary>
        <ul>
          <li v-for="page in extractionBatch.pages">
            {{ t('page', page) }}
            <ul>
              <li>{{ t('timing.extraction') }} {{ showDuration(page.timing.extraction) }}</li>
              <li>{{ t('timing.classification') }} {{ showDuration(page.timing.classification) }}</li>
              <li v-for="(adaptationTiming, index) in page.timing.adaptations">
                {{ t('timing.adaptation', { index: index + 1 }) }} {{ showDuration(adaptationTiming) }}
              </li>
            </ul>
          </li>
        </ul>
      </details>
      <template v-for="page in extractionBatch.pages" :key="page.pageNumber">
        <h2>
          {{ t('page', page) }}
          <template v-if="page.assistantResponse === null"
            ><WhiteSpace /><span class="inProgress">{{ t('inProgress') }}</span></template
          >
        </h2>
        <h3>{{ t('images') }}</h3>
        <p v-if="Object.keys(page.imagesUrls).length === 0">{{ t('noImages') }}</p>
        <p v-else>
          <template v-for="(imageUrl, imageIdentifier) in page.imagesUrls">
            <span style="display: inline-block; margin-right: 1em; margin-bottom: 1em; text-align: center">
              <img :src="imageUrl" style="max-height: 4em" />
              <br />
              {{ imageIdentifier }}
            </span>
          </template>
        </p>
        <template v-if="page.assistantResponse !== null">
          <template v-if="page.assistantResponse.kind === 'success'">
            <template v-for="exercise in page.exercises" :key="exercise.exerciseNumber">
              <AdaptableExercisePreview
                :headerLevel="3"
                context="extraction"
                :index="null"
                :exercise
                @batchUpdated="emit('batch-updated')"
                @submitExtractionsWithRecentSettings="submitAdaptationsWithRecentSettings"
              />
            </template>
          </template>
          <template v-else-if="page.assistantResponse.kind === 'error'">
            <template v-if="page.assistantResponse.error === 'not-json'">
              <p>{{ t('notJsonError') }}</p>
              <pre>{{ page.assistantResponse.text }}</pre>
            </template>
            <template v-else-if="page.assistantResponse.error === 'invalid-json'">
              <p>{{ t('invalidJsonError') }}</p>
              <pre>{{ jsonStringifyPrettyCompact(page.assistantResponse.parsed) }}</pre>
            </template>
            <p v-else-if="page.assistantResponse.error === 'unknown'">{{ t('unknownError') }}</p>
            <p v-else>BUG: {{ ((r: never) => r)(page.assistantResponse) }}</p>
          </template>
          <p v-else>BUG: {{ ((r: never) => r)(page.assistantResponse) }}</p>
        </template>
      </template>
    </template>
  </ResizableColumns>
</template>

<i18n>
en:
  createdBy: "Created by:"
  strategy: Strategy
  llmModel: LLM model
  settings: Settings
  prompt: Prompt
  download: Download {0}, {1}, {2}, {3}, {4}, or {5}
  standaloneHtml: standalone HTML
  jsonDataForExtractedExercises: JSON data for extracted exercises
  tsvDataForExtractedExercises: TSV data for extracted exercises
  tsvDataForClassifiedExercises: TSV data for classified exercises
  jsonDataForAdaptedExercises: JSON data for adapted exercises
  zipDataForAdaptedExercises: JSON/ZIP data for adapted exercises
  followUps: Follow-ups
  runClassification: "Run classification after extraction:"
  runClassificationYesUsing: "yes, using {0}, provided by {1} by e-mail on {2}"
  runAdaptation: "Run adaptations after classification:"
  runAdaptationYesUsing: "yes, using {0} with the latest settings for each known exercise class"
  runAdaptationUsingProvider: "provider"
  runAdaptationUsingModel: "and model"
  no: no
  result: Result
  timing:
    summary: Click to see timing information
    extraction: "Extraction:"
    classification: "Classification:"
    adaptation: "Adaptation {index}:"
  page: Page {pageNumber}
  images: Images
  noImages: "None."
  inProgress: "(in progress, will refresh when done)"
  notJsonError: "The LLM returned a response that is not correct JSON."
  invalidJsonError: "The LLM returned a JSON response that does not validate against the extracted exercises list schema."
  unknownError: "The LLM caused an unknown error."
  change: 🖊️ change
  submit: Submit
fr:
  createdBy: "Créé par :"
  strategy: Stratégie
  llmModel: Modèle LLM
  settings: Paramètres
  prompt: Invite
  download: Télécharger {0}, {1}, {2}, {3}, {4}, ou {5}
  standaloneHtml: le HTML autonome
  jsonDataForExtractedExercises: les données JSON des exercices extraits
  tsvDataForExtractedExercises: les données TSV des exercices extraits
  tsvDataForClassifiedExercises: les données TSV des exercices classifiés
  jsonDataForAdaptedExercises: les données JSON des exercices adaptés
  zipDataForAdaptedExercises: les données JSON/ZIP des exercices adaptés
  followUps: Étapes suivantes
  runClassification: "Exécuter la classification après l'extraction :"
  runClassificationYesUsing: "oui, avec {0}, fourni par {1} par e-mail le {2}"
  runAdaptation: "Exécuter les adaptations après la classification :"
  runAdaptationYesUsing: "oui, avec {0} avec les derniers paramètres pour chaque classe d'exercice connue"
  runAdaptationUsingProvider: "fournisseur"
  runAdaptationUsingModel: "et modèle"
  no: non
  result: Résultat
  timing:
    summary: Cliquez pour voir les informations de chronométrage
    extraction: "Extraction :"
    classification: "Classification :"
    adaptation: "Adaptation {index} :"
  page: Page {pageNumber}
  images: Images
  noImages: "Aucune."
  inProgress: "(en cours, se mettra à jour quand terminé)"
  notJsonError: "Le LLM a renvoyé une réponse qui n'est pas un JSON correct."
  invalidJsonError: "Le LLM a renvoyé une réponse JSON qui ne correspond pas au schéma d'une liste d'exercices extraits."
  unknownError: "Le LLM a causé une erreur inconnue."
  change: 🖊️ modifier
  submit: Soumettre
</i18n>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
