<script setup lang="ts">
import { type ClassificationBatch } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import EditClassificationBatchFormExercisePreview from './EditClassificationBatchFormExercisePreview.vue'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'

defineProps<{
  classificationBatch: ClassificationBatch
}>()

const authenticationTokenStore = useAuthenticationTokenStore()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ classificationBatch.createdBy }}</p>
  <p>Classification model: <code>classification_camembert.pt</code>, provided by Elise by e-mail on 2025-05-20</p>
  <p>
    Class names produced: <code>Associe</code>, <code>AssocieCoche</code>, <code>CM</code>, <code>CacheIntrus</code>,
    <code>Classe</code>, <code>ClasseCM</code>, <code>CliqueEcrire</code>, <code>CocheGroupeMots</code>,
    <code>CocheIntrus</code>, <code>CocheLettre</code>, <code>CocheMot</code>, <code>CocheMot*</code>,
    <code>CochePhrase</code>, <code>Echange</code>, <code>EditPhrase</code>, <code>EditTexte</code>,
    <code>ExpressionEcrite</code>, <code>GenreNombre</code>, <code>Phrases</code>, <code>Question</code>,
    <code>RC</code>, <code>RCCadre</code>, <code>RCDouble</code>, <code>RCImage</code>, <code>Texte</code>,
    <code>Trait</code>, <code>TransformeMot</code>, <code>TransformePhrase</code>, <code>VraiFaux</code>
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
    <a
      :href="`/api/export/classification-batch/${classificationBatch.id}.html?token=${authenticationTokenStore.token}`"
    >
      Download standalone HTML
    </a>
  </p>
  <h1>Inputs</h1>
  <template v-for="(exercise, index) in classificationBatch.exercises">
    <EditClassificationBatchFormExercisePreview
      header="h2"
      :adaptationWasRequested="classificationBatch.modelForAdaptation !== null"
      :exercise
      :index
    />
  </template>
</template>
