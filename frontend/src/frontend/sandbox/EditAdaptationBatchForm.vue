<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { type AdaptationBatch } from '@/frontend/ApiClient'
import ResizableColumns from '$/ResizableColumns.vue'
import AdaptationStrategyEditor from '@/frontend/common/AdaptationStrategyEditor.vue'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'

defineProps<{
  adaptationBatch: AdaptationBatch
}>()

const { t } = useI18n()
const authenticationTokenStore = useAuthenticationTokenStore()

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
      <p>{{ t('createdBy') }} {{ adaptationBatch.createdBy }}</p>
      <AdaptationStrategyEditor
        :availableStrategySettings="[]"
        :disabled="true"
        :modelValue="adaptationBatch.strategy"
      />
    </template>
    <template #col-2>
      <p>
        <RouterLink :to="{ name: 'create-adaptation-batch', query: { base: adaptationBatch.id } }">
          {{ t('newBatchBasedOnThisOne') }}
        </RouterLink>
      </p>
      <p>
        <I18nT keypath="download">
          <a
            :href="`/api/export/sandbox-adaptation-batch-${adaptationBatch.id}.html?token=${authenticationTokenStore.token}`"
          >
            {{ t('standaloneHtml') }}
          </a>
          <a
            :href="`/api/export/sandbox-adaptation-batch-${adaptationBatch.id}-adapted-exercises.json?token=${authenticationTokenStore.token}`"
          >
            {{ t('jsonDataForAdaptedExercises') }}
          </a>
          <a
            :href="`/api/export/sandbox-adaptation-batch-${adaptationBatch.id}-adapted-exercises.zip?token=${authenticationTokenStore.token}`"
          >
            {{ t('zipDataForAdaptedExercises') }}
          </a>
        </I18nT>
      </p>
      <details>
        <summary>{{ t('timing.summary') }}</summary>
        <ul>
          <li v-for="(adaptationTiming, index) in adaptationBatch.timing.adaptations">
            {{ t('timing.adaptation', { index: index + 1 }) }} {{ showDuration(adaptationTiming) }}
          </li>
        </ul>
      </details>

      <h1>{{ t('inputs') }}</h1>
      <AdaptableExercisePreview
        v-for="(exercise, index) in adaptationBatch.exercises"
        :headerLevel="2"
        context="adaptation"
        :index
        :exercise
      />
    </template>
  </ResizableColumns>
</template>

<i18n>
en:
  createdBy: "Created by:"
  newBatchBasedOnThisOne: New batch based on this one
  download: Download {0}, {1}, or {2}
  standaloneHtml: standalone HTML
  jsonDataForAdaptedExercises: JSON data for adapted exercises
  zipDataForAdaptedExercises: JSON/ZIP data for adapted exercises
  timing:
    summary: Click to see timing information
    adaptation: "Adaptation {index}:"
  inputs: Inputs
fr:
  createdBy: "Créé par :"
  newBatchBasedOnThisOne: Nouveau batch basé sur celui-ci
  download: Télécharger {0}, {1}, ou {2}
  standaloneHtml: le HTML autonome
  jsonDataForAdaptedExercises: les données JSON des exercices adaptés
  zipDataForAdaptedExercises: les données JSON/ZIP des exercices adaptés
  timing:
    summary: Cliquez pour voir les informations de chronométrage
    adaptation: "Adaptation {index} :"
  inputs: Entrées
</i18n>
