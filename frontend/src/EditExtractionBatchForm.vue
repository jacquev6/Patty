<script setup lang="ts">
import { type ExtractionBatch } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from './WhiteSpace.vue'
import EditClassificationBatchFormExercisePreview from './EditClassificationBatchFormExercisePreview.vue'

defineProps<{
  extractionBatch: ExtractionBatch
}>()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ extractionBatch.createdBy }}</p>
  <p>
    <a :href="`/api/export/extraction-batch/${extractionBatch.id}.html?token=${authenticationTokenStore.token}`">
      Download standalone HTML
    </a>
  </p>
  <h1>Result</h1>
  <template v-for="page in extractionBatch.pages" :key="page.pageNumber">
    <h2>
      Page {{ page.pageNumber
      }}<template v-if="!page.done"
        ><WhiteSpace /><span class="inProgress">(in progress, will refresh when done)</span></template
      >
    </h2>
    <template v-for="(exercise, index) in page.exercises" :key="exercise.exerciseNumber">
      <EditClassificationBatchFormExercisePreview
        header="h3"
        :adaptationWasRequested="extractionBatch.modelForAdaptation !== null"
        :exercise
        :index
      >
        <h3>Exercise {{ exercise.exerciseNumber }}</h3>
      </EditClassificationBatchFormExercisePreview>
    </template>
  </template>
</template>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
