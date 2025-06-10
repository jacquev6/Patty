<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type AdaptationLlmModel, useAuthenticatedClient } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputsEditor from './CreateClassificationBatchFormInputsEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

const props = defineProps<{
  availableAdaptationLlmModels: AdaptationLlmModel[]
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const runAdaptationAsString = ref('yes')

const llmModel = ref(props.availableAdaptationLlmModels[0])

const runAdaptation = computed(() => runAdaptationAsString.value === 'yes')

const inputs = reactive<InputWithFile[]>([])

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.instructionHintExampleText.trim() !== '' || input.statementText.trim() !== '')
    .map(({ pageNumber, exerciseNumber, instructionHintExampleText, statementText }) => ({
      pageNumber,
      exerciseNumber,
      instructionHintExampleText,
      statementText,
    })),
)

const disabled = computed(() => cleanedUpInputs.value.length === 0)

async function submit() {
  const response = await client.POST('/api/classification-batches', {
    body: {
      creator: identifiedUser.identifier,
      inputs: cleanedUpInputs.value,
      modelForAdaptation: runAdaptation.value ? llmModel.value : null,
    },
  })
  if (response.data !== undefined) {
    router.push({ name: 'classification-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p>Classification model: <code>classification_camembert.pt</code>, provided by Elise by e-mail on 2025-05-20</p>
  <p>
    Class names produced: <code>Associe</code>, <code>AssocieCoche</code>, <code>CM</code>, <code>CacheIntrus</code>,
    <code>Classe</code>, <code>ClasseCM</code>, <code>CliqueEcrire</code>, <code>CocheGroupeMots</code>,
    <code>CocheIntrus</code>, <code>CocheLettre</code>, <code>CocheMot</code>, <code>CocheMot</code>",
    <code>CochePhrase</code>, <code>Echange</code>, <code>EditPhrase</code>, <code>EditTexte</code>,
    <code>ExpressionEcrite</code>, <code>GenreNombre</code>, <code>Phrases</code>, <code>Question</code>,
    <code>RC</code>, <code>RCCadre</code>, <code>RCDouble</code>, <code>RCImage</code>, <code>Texte</code>,
    <code>Trait</code>, <code>TransformeMot</code>, <code>TransformePhrase</code>,
    <code>VraiFaux</code>
  </p>
  <p>
    Run adaptations after classification:
    <select data-cy="run-adaptation" v-model="runAdaptationAsString">
      <option>yes</option>
      <option>no</option>
    </select>
    <template v-if="runAdaptation">
      using
      <LlmModelSelector :availableLlmModels="availableAdaptationLlmModels" :disabled="false" v-model="llmModel">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each known exercise class.</template
    >
  </p>
  <h1>Inputs</h1>
  <p><button @click="submit" :disabled>Submit</button></p>
  <CreateClassificationBatchFormInputsEditor headers="h2" v-model="inputs" />
</template>
