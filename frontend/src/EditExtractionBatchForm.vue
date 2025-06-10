<script setup lang="ts">
import { type ExtractionBatch } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from './WhiteSpace.vue'
import EditClassificationBatchFormExercisePreview from './EditClassificationBatchFormExercisePreview.vue'
import LlmModelSelector from './LlmModelSelector.vue'

defineProps<{
  extractionBatch: ExtractionBatch
}>()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ extractionBatch.createdBy }}</p>
  <p>
    Run classification after extraction:
    <template v-if="extractionBatch.runClassification"
      >yes, using <code>classification_camembert.pt</code>, provided by Elise by e-mail on 2025-05-20</template
    >
    <template v-else>no</template>
  </p>
  <p v-if="extractionBatch.runClassification">
    Run adaptations after classification:
    <template v-if="extractionBatch.modelForAdaptation === null">no</template>
    <template v-else
      >yes, using
      <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="extractionBatch.modelForAdaptation">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each known exercise class.</template
    >
  </p>
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
        <h3>
          Exercise {{ exercise.exerciseNumber
          }}<span v-if="exercise.exerciseClass === null" class="inProgress">
            (in progress, will refresh when done) </span
          ><template v-else>: {{ exercise.exerciseClass }} </template>
        </h3>
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
