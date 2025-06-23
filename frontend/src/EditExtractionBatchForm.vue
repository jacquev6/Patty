<script setup lang="ts">
import jsonStringifyPrettyCompact from 'json-stringify-pretty-compact'

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

const apiConstantsStore = useApiConstantsStore()

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
      <AdaptedExerciseJsonSchemaDetails :schema="apiConstantsStore.extractionLlmResponseSchema" />
      <h3>Prompt</h3>
      <MarkDown :markdown="extractionBatch.strategy.prompt" />
    </template>
    <template #col-2>
      <p>
        Download
        <a :href="`/api/export/extraction-batch/${extractionBatch.id}.html?token=${authenticationTokenStore.token}`"
          >standalone HTML</a
        >
        or
        <a :href="`/api/export/extraction-batch/${extractionBatch.id}.json?token=${authenticationTokenStore.token}`"
          >JSON data</a
        >
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
          }}<template v-if="page.assistantResponse === null"
            ><WhiteSpace /><span class="inProgress">(in progress, will refresh when done)</span></template
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
              <p>The LLM returned a response that is not correct JSON.</p>
              <pre>{{ page.assistantResponse.text }}</pre>
            </template>
            <template v-else-if="page.assistantResponse.error === 'invalid-json'">
              <p>
                The LLM returned a JSON response that does not validate against the extracted exercises list schema.
              </p>
              <pre>{{ jsonStringifyPrettyCompact(page.assistantResponse.parsed) }}</pre>
            </template>
            <p v-else-if="page.assistantResponse.error === 'unknown'">The LLM caused an unknown error.</p>
            <p v-else>Unexpected assistant error response: {{ ((r: never) => r)(page.assistantResponse) }}</p>
          </template>
          <p v-else>Unexpected assistant response: {{ ((r: never) => r)(page.assistantResponse) }}</p>
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
