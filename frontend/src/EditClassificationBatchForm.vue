<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { type ClassificationBatch } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import EditClassificationOrExtractionBatchFormExercisePreview from './EditClassificationOrExtractionBatchFormExercisePreview.vue'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import classificationCamembert20250520 from './ClassificationCamembert20250520'

defineProps<{
  classificationBatch: ClassificationBatch
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const { d } = useI18n({ useScope: 'global' })

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ classificationBatch.createdBy }}</p>
  <p>
    Classification model: <code>{{ classificationCamembert20250520.fileName }}</code
    >, provided by {{ classificationCamembert20250520.providedBy }} by e-mail on
    {{ d(classificationCamembert20250520.providedOn, 'long-date') }}
  </p>
  <p>
    Class names produced:
    <template v-for="(className, index) in classificationCamembert20250520.classesProduced">
      <template v-if="index !== 0">, </template>
      <code>{{ className }}</code>
    </template>
  </p>
  <p>
    Run adaptation after classification:
    <template v-if="classificationBatch.modelForAdaptation === null">no</template>
    <template v-else
      >yes, using
      <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="classificationBatch.modelForAdaptation">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each known exercise class.</template
    >
  </p>
  <p>
    Download
    <a :href="`/api/export/classification-batch/${classificationBatch.id}.html?token=${authenticationTokenStore.token}`"
      >standalone HTML</a
    >
    or
    <a :href="`/api/export/classification-batch/${classificationBatch.id}.json?token=${authenticationTokenStore.token}`"
      >JSON data</a
    >
  </p>
  <h1>Inputs</h1>
  <template v-for="(exercise, index) in classificationBatch.exercises">
    <EditClassificationOrExtractionBatchFormExercisePreview
      headerComponent="h2"
      :headerText="`Input ${index + 1}`"
      :showPageAndExercise="true"
      :classificationWasRequested="true"
      :adaptationWasRequested="classificationBatch.modelForAdaptation !== null"
      :exercise
      @batchUpdated="emit('batch-updated')"
    />
  </template>
</template>
