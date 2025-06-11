<script setup lang="ts">
import { type ExtractionBatch } from './apiClient'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import WhiteSpace from './WhiteSpace.vue'
import EditClassificationBatchFormExercisePreview from './EditClassificationBatchFormExercisePreview.vue'
import LlmModelSelector from './LlmModelSelector.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import MarkDown from './MarkDown.vue'

defineProps<{
  extractionBatch: ExtractionBatch
  extractionLlmResponseSchema: Record<string, never>
}>()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <ResizableColumns :columns="[1, 2]">
    <template #col-1>
      <p>Created by: {{ extractionBatch.createdBy }}</p>
      <h1>Strategy</h1>
      <h2>LLM model</h2>
      <p><LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="extractionBatch.strategy.model" /></p>
      <h2>Settings</h2>
      <AdaptedExerciseJsonSchemaDetails :schema="extractionLlmResponseSchema" />
      <h3>Prompt</h3>
      <MarkDown :markdown="extractionBatch.strategy.prompt" />
    </template>
    <template #col-2>
      <p>
        <a :href="`/api/export/extraction-batch/${extractionBatch.id}.html?token=${authenticationTokenStore.token}`">
          Download standalone HTML
        </a>
      </p>
      <h1>Follow-ups</h1>
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
  </ResizableColumns>
</template>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
