<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

import { useAuthenticatedClient, type ClassificationBatch } from '@/frontend/ApiClient'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import classificationCamembert20250520 from '@/frontend/sandbox/ClassificationCamembert20250520'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '$/WhiteSpace.vue'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'

const props = defineProps<{
  classificationBatch: ClassificationBatch
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()

const authenticationTokenStore = useAuthenticationTokenStore()

const editingModelForAdaptation = ref(false)
const apiConstantsStore = useApiConstantsStore()
const llmModelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])
async function submitAdaptation() {
  editingModelForAdaptation.value = false
  await client.PUT('/api/classification-batches/{id}/model-for-adaptation', {
    params: { path: { id: props.classificationBatch.id } },
    body: llmModelForAdaptation.value,
  })
  emit('batch-updated')
}

async function submitAdaptationsWithRecentSettings() {
  await client.POST('/api/classification-batches/{id}/submit-adaptations-with-recent-settings', {
    params: { path: { id: props.classificationBatch.id } },
  })

  emit('batch-updated')
}

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
  <h1>{{ t('settings') }}</h1>
  <p>{{ t('createdBy') }} {{ classificationBatch.createdBy }}</p>
  <p>
    {{ t('classNamesProduced') }}
    <template v-for="(className, index) in classificationCamembert20250520.classesProduced">
      <template v-if="index !== 0">, </template>
      <code>{{ className }}</code>
    </template>
  </p>
  <p>
    {{ t('runAdaptation') }}
    <template v-if="classificationBatch.modelForAdaptation === null">
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
        <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="llmModelForAdaptation">
          <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
          <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
        </LlmModelSelector> </I18nT
      >.
    </template>
  </p>
  <p>
    <I18nT keypath="download">
      <a
        :href="`/api/export/sandbox-classification-batch-${classificationBatch.id}.html?token=${authenticationTokenStore.token}`"
      >
        {{ t('standaloneHtml') }}
      </a>
      <a
        :href="`/api/export/sandbox-classification-batch-${classificationBatch.id}-classified-exercises.tsv?token=${authenticationTokenStore.token}`"
      >
        {{ t('tsvDataForClassifiedExercises') }}
      </a>
      <a
        :href="`/api/export/sandbox-classification-batch-${classificationBatch.id}-adapted-exercises.json?token=${authenticationTokenStore.token}`"
      >
        {{ t('jsonDataForAdaptedExercises') }}
      </a>
      <a
        :href="`/api/export/sandbox-classification-batch-${classificationBatch.id}-adapted-exercises.zip?token=${authenticationTokenStore.token}`"
      >
        {{ t('zipDataForAdaptedExercises') }}
      </a>
    </I18nT>
  </p>
  <details>
    <summary>{{ t('timing.summary') }}</summary>
    <ul>
      <li>{{ t('timing.classification') }} {{ showDuration(classificationBatch.timing.classification) }}</li>
      <li v-for="(adaptationTiming, index) in classificationBatch.timing.adaptations">
        {{ t('timing.adaptation', { index: index + 1 }) }} {{ showDuration(adaptationTiming) }}
      </li>
    </ul>
  </details>

  <h1>{{ t('inputs') }}</h1>
  <template v-for="(exercise, index) in classificationBatch.exercises">
    <AdaptableExercisePreview
      :headerLevel="2"
      context="classification"
      :index
      :exercise
      @batchUpdated="emit('batch-updated')"
      @submitExtractionsWithRecentSettings="submitAdaptationsWithRecentSettings"
    />
  </template>
</template>

<i18n>
en:
  settings: Settings
  createdBy: "Created by:"
  classNamesProduced: "Class names produced:"
  change: 🖊️ change
  runAdaptation: "Run adaptation after classification:"
  runAdaptationYesUsing: "yes, using {0} with the latest settings for each known exercise class"
  runAdaptationUsingProvider: provider
  runAdaptationUsingModel: and model
  no: no
  submit: Submit
  download: Download {0}, {1}, {2}, or {3}
  standaloneHtml: standalone HTML
  tsvDataForClassifiedExercises: TSV data for classified exercises
  jsonDataForAdaptedExercises: JSON data for adapted exercises
  zipDataForAdaptedExercises: JSON/ZIP data for adapted exercises
  inputs: Inputs
  timing:
    summary: Click to see timing information
    classification: "Classification:"
    adaptation: "Adaptation {index}:"
fr:
  settings: Paramètres
  createdBy: "Créé par :"
  classNamesProduced: "Noms de classe produits :"
  change: 🖊️ modifier
  runAdaptation: "Exécuter l'adaptation après la classification :"
  runAdaptationYesUsing: "oui, en utilisant {0} avec les derniers paramètres pour chaque classe d'exercice connue"
  runAdaptationUsingProvider: fournisseur
  runAdaptationUsingModel: et modèle
  no: non
  submit: Soumettre
  download: Télécharger {0}, {1}, {2}, ou {3}
  standaloneHtml: le HTML autonome
  tsvDataForClassifiedExercises: les données TSV des exercices classifiés
  jsonDataForAdaptedExercises: les données JSON des exercices adaptés
  zipDataForAdaptedExercises: les données JSON/ZIP des exercices adaptés
  inputs: Entrées
  timing:
    summary: Cliquez pour voir les informations de chronométrage
    classification: "Classification :"
    adaptation: "Adaptation {index} :"
</i18n>
