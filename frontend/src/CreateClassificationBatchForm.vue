<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

import { type LlmModel } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputsEditor from './CreateClassificationBatchFormInputsEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'

const props = defineProps<{
  availableLlmModels: LlmModel[]
}>()

const runAdaptationAsString = ref('yes')

const llmModel = ref(props.availableLlmModels[0])

const runAdaptation = computed(() => runAdaptationAsString.value === 'yes')

const inputs = reactive<InputWithFile[]>([])

function submit() {}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p>
    Run adaptations after classification:
    <select v-model="runAdaptationAsString">
      <option>yes</option>
      <option>no</option>
    </select>
    <template v-if="runAdaptation">
      using
      <LlmModelSelector :availableLlmModels :disabled="false" v-model="llmModel">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each class.</template
    >
  </p>
  <h1>Inputs</h1>
  <p><button @click="submit">Submit</button></p>
  <CreateClassificationBatchFormInputsEditor headers="h2" v-model="inputs" />
</template>
