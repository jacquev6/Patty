<script setup lang="ts">
import jsonStringifyPrettyCompact from 'json-stringify-pretty-compact'
import { useI18n } from 'vue-i18n'

import { type ExtractionBatch } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from './WhiteSpace.vue'
import EditClassificationOrExtractionBatchFormExercisePreview from './EditClassificationOrExtractionBatchFormExercisePreview.vue'
import LlmModelSelector from './LlmModelSelector.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import MarkDown from './MarkDown.vue'
import { useApiConstantsStore } from './ApiConstantsStore'

defineProps<{
  extractionBatch: ExtractionBatch
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const { t } = useI18n()
const apiConstantsStore = useApiConstantsStore()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <ResizableColumns :columns="[1, 2]">
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
            :href="`/api/export/extraction-batch/${extractionBatch.id}.html?token=${authenticationTokenStore.token}`"
            >{{ t('standaloneHtml') }}</a
          >
          <a
            :href="`/api/export/extraction-batch/${extractionBatch.id}.json?token=${authenticationTokenStore.token}`"
            >{{ t('jsonData') }}</a
          >
        </I18nT>
      </p>
      <h1>{{ t('followUps') }}</h1>
      <p>
        {{ t('runClassification') }}
        <template v-if="extractionBatch.runClassification">
          <I18nT keypath="runClassificationYesUsing"><code>classification_camembert.pt</code></I18nT>
        </template>
        <template v-else>{{ t('no') }}</template>
      </p>
      <p v-if="extractionBatch.runClassification">
        {{ t('runAdaptation') }}
        <template v-if="extractionBatch.modelForAdaptation === null">{{ t('no') }}</template>
        <template v-else>
          <I18nT keypath="runAdaptationYesUsing">
            <LlmModelSelector
              :availableLlmModels="[]"
              :disabled="true"
              :modelValue="extractionBatch.modelForAdaptation"
            >
              <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
              <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
            </LlmModelSelector>
          </I18nT>
        </template>
      </p>
      <h1>{{ t('result') }}</h1>
      <template v-for="page in extractionBatch.pages" :key="page.pageNumber">
        <h2>
          {{ t('page', page) }}
          <template v-if="page.assistantResponse === null"
            ><WhiteSpace /><span class="inProgress">{{ t('inProgress') }}</span></template
          >
        </h2>
        <template v-if="page.assistantResponse !== null">
          <template v-if="page.assistantResponse.kind === 'success'">
            <template v-for="(exercise, index) in page.exercises" :key="exercise.exerciseNumber">
              <EditClassificationOrExtractionBatchFormExercisePreview
                headerComponent="h3"
                :headerText="`Exercise ${index + 1}`"
                :showPageAndExercise="false"
                :classificationWasRequested="extractionBatch.runClassification"
                :adaptationWasRequested="extractionBatch.modelForAdaptation !== null"
                :exercise
                @batchUpdated="emit('batch-updated')"
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
            <p v-else>Unexpected assistant error response: {{ ((r: never) => r)(page.assistantResponse) }}</p>
          </template>
          <p v-else>Unexpected assistant response: {{ ((r: never) => r)(page.assistantResponse) }}</p>
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
  download: Download {0} or {1}
  standaloneHtml: "standalone HTML"
  jsonData: "JSON data"
  followUps: Follow-ups
  runClassification: "Run classification after extraction:"
  runClassificationYesUsing: "yes, using {0}, provided by Elise by e-mail on May 20, 2025"
  runAdaptation: "Run adaptations after classification:"
  runAdaptationYesUsing: "yes, using {0} with the latest settings for each known exercise class."
  runAdaptationUsingProvider: "provider"
  runAdaptationUsingModel: "and model"
  no: no
  result: Result
  page: Page {pageNumber}
  inProgress: "(in progress, will refresh when done)"
  notJsonError: "The LLM returned a response that is not correct JSON."
  invalidJsonError: "The LLM returned a JSON response that does not validate against the extracted exercises list schema."
  unknownError: "The LLM caused an unknown error."
fr:
  createdBy: "Créé par :"
  strategy: Stratégie
  llmModel: Modèle LLM
  settings: Paramètres
  prompt: Invite
  download: Télécharger le {0} ou les {1}
  standaloneHtml: "HTML autonome"
  jsonData: "données JSON"
  followUps: Étapes suivantes
  runClassification: "Exécuter la classification après l'extraction :"
  runClassificationYesUsing: "oui, avec {0}, fourni par Elise par e-mail le 20 mai 2025"
  runAdaptation: "Exécuter les adaptations après la classification :"
  runAdaptationYesUsing: "oui, avec {0} avec les derniers paramètres pour chaque classe d'exercice connue."
  runAdaptationUsingProvider: "fournisseur"
  runAdaptationUsingModel: "et modèle"
  no: non
  result: Résultat
  page: Page {pageNumber}
  inProgress: "(en cours, se mettra à jour quand terminé)"
  notJsonError: "Le LLM a renvoyé une réponse qui n'est pas un JSON correct."
  invalidJsonError: "Le LLM a renvoyé une réponse JSON qui ne correspond pas au schéma d'une liste d'exercices extraits."
  unknownError: "Le LLM a causé une erreur inconnue."
</i18n>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
