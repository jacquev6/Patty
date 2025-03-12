<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useApiClient, type Tokenization } from './apiClient'
import TokenizationRender from './TokenizationRender.vue'

const props = defineProps<{
  id: string
}>()

const client = useApiClient()

const tokenization = ref<Tokenization | null>(null)

onMounted(async () => {
  const response = await client.GET(`/api/tokenization/{id}`, { params: { path: { id: props.id } } })

  if (response.data !== undefined) {
    tokenization.value = response.data
  }
})

const adjustment = ref('')
const disabled = ref(false)

async function submit() {
  disabled.value = true

  const responsePromise = client.POST(`/api/tokenization/{id}/adjustment`, {
    params: { path: { id: props.id } },
    body: { adjustment: adjustment.value },
  })

  adjustment.value = ''
  const response = await responsePromise
  disabled.value = false

  if (response.data !== undefined) {
    tokenization.value = response.data
  }
}

async function rewindLastStep() {
  disabled.value = true

  const responsePromise = client.DELETE(`/api/tokenization/{id}/last-step`, {
    params: { path: { id: props.id } },
  })

  const response = await responsePromise
  disabled.value = false
  if (response.data !== undefined) {
    tokenization.value = response.data
  }
}
</script>

<template>
  <p><RouterLink :to="{ name: 'create-tokenization' }">New tokenization</RouterLink></p>
  <template v-if="tokenization !== null">
    <h1>LLM provider and model name</h1>
    <p>
      {{ tokenization.llm_provider }}:
      {{ tokenization.llm_provider === 'mistralai' ? tokenization.mistralai_model : tokenization.openai_model }}
    </p>
    <div v-for="(step, stepIndex) in tokenization.steps" class="step">
      <div class="columns">
        <div class="column">
          <template v-if="step.kind == 'initial'">
            <h1>System prompt</h1>
            <pre>{{ step.system_prompt }}</pre>
            <h1>Input text</h1>
            <pre>{{ step.input_text }}</pre>
            <h1>Assistant's response</h1>
            <pre>{{ step.assistant_prose }}</pre>
            <h1>Tokenized text</h1>
            <p v-if="step.tokenized_text === null">No changes</p>
            <TokenizationRender v-else :tokenizedText="step.tokenized_text" />
          </template>
          <template v-else-if="step.kind == 'adjustment'">
            <h1>User-requested adjustment</h1>
            <pre>{{ step.user_prompt }}</pre>
            <h1>Assistant's response</h1>
            <pre>{{ step.assistant_prose }}</pre>
            <h1>Tokenized text</h1>
            <p v-if="step.tokenized_text === null">No changes</p>
            <TokenizationRender v-else :tokenizedText="step.tokenized_text" />
          </template>
          <template v-else>BUG: {{ ((step: never) => step)(step) }}</template>
          <template v-if="stepIndex === tokenization.steps.length - 1">
            <button @click="rewindLastStep">Rewind this step</button>
          </template>
        </div>
        <div class="column">
          <h1>LLM messages</h1>
          <pre>{{ step.messages }}</pre>
        </div>
      </div>
    </div>
    <h1>Adjustments</h1>
    <textarea v-model="adjustment" rows="5" cols="80" :disabled></textarea>
    <p><button @click="submit" :disabled>Submit</button></p>
  </template>
</template>

<style scoped>
.step {
  margin-bottom: 5px;
}

.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.column {
  border: 1px solid black;
  padding: 5px;
  overflow-x: scroll;
}
</style>
