<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'

import { client, type Tokenization } from './apiClient'
import TokenizationRender from './TokenizationRender.vue'
import ThreeColumns from './ThreeColumns.vue'
import TextArea from './TextArea.vue'
import assert from './assert'
import MarkDown from './MarkDown.vue'
import Busy from './BusyBox.vue'

const props = defineProps<{
  id: string
}>()

const tokenization = ref<Tokenization | null>(null)

onMounted(async () => {
  const response = await client.GET(`/api/tokenization/{id}`, { params: { path: { id: props.id } } })

  if (response.data !== undefined) {
    tokenization.value = response.data
  }
})

const systemPrompt = computed(() => {
  if (tokenization.value === null) {
    return ''
  } else {
    assert(tokenization.value.steps.length > 0)
    assert(tokenization.value.steps[0].kind === 'initial')
    return tokenization.value.steps[0].system_prompt
  }
})

const inputText = computed(() => {
  if (tokenization.value === null) {
    return ''
  } else {
    assert(tokenization.value.steps.length > 0)
    assert(tokenization.value.steps[0].kind === 'initial')
    return tokenization.value.steps[0].input_text
  }
})

const llmTokenizedText = computed(() => {
  const empty = { sentences: [] }
  if (tokenization.value === null) {
    return empty
  } else {
    assert(tokenization.value.steps.length > 0)
    return tokenization.value.steps.map((step) => step.tokenized_text).reduce((old, now) => now ?? old) ?? empty
  }
})

const tokenizedText = computed(() => {
  if (manualTokenizedText.value !== null) {
    // @todo Catch JSON parse error
    // @todo Validate against JSON schema
    // @todo Report these errors to the user
    return JSON.parse(manualTokenizedText.value)
  } else {
    return llmTokenizedText.value
  }
})

const manualTokenizedText = ref<string | null>(null)

const manualTokenizedTextProxy = computed({
  get() {
    if (manualTokenizedText.value === null) {
      return jsonStringify(tokenizedText.value)
    } else {
      return manualTokenizedText.value
    }
  },
  set(value: string) {
    manualTokenizedText.value = value
  },
})

const adjustment = ref('')
const disabled = computed(() => adjustment.value.trim() === '' || manualTokenizedText.value !== null)
const busy = ref(false)

async function submit() {
  busy.value = true

  const responsePromise = client.POST(`/api/tokenization/{id}/adjustment`, {
    params: { path: { id: props.id } },
    body: { adjustment: adjustment.value },
  })

  adjustment.value = ''
  const response = await responsePromise

  if (response.data !== undefined) {
    tokenization.value = response.data
  }

  busy.value = false
}

async function rewindLastStep() {
  const responsePromise = client.DELETE(`/api/tokenization/{id}/last-step`, {
    params: { path: { id: props.id } },
  })

  const response = await responsePromise
  if (response.data !== undefined) {
    tokenization.value = response.data
  }
}
</script>

<template>
  <ThreeColumns v-if="tokenization !== null">
    <template #left>
      <h1>LLM model</h1>
      <p>{{ tokenization.llm_model.provider }}: {{ tokenization.llm_model.name }}</p>
      <h1>System prompt</h1>
      <MarkDown :markdown="systemPrompt" />
    </template>
    <template #center>
      <!-- @todo Offer to display the low level messages exchanged with the LLM -->
      <h1>Input text</h1>
      <MarkDown :markdown="inputText" />
      <h1>Adjustments</h1>
      <Busy :busy>
        <template v-for="(step, stepIndex) in tokenization.steps">
          <div v-if="step.kind === 'adjustment'" style="display: flex" class="user-prompt">
            <MarkDown :markdown="step.user_prompt" style="flex-grow: 1" />
            <div
              v-if="stepIndex === tokenization.steps.length - 1"
              title="Rewind the chat: delete this prompt and its effects"
              style="cursor: pointer"
              @click="rewindLastStep"
            >
              ❌
            </div>
          </div>
          <MarkDown class="assistant-prose" :markdown="step.assistant_prose" />
        </template>
        <div v-if="manualTokenizedText === null" class="user-prompt">
          <TextArea v-model="adjustment"></TextArea>
          <p><button @click="submit" :disabled>Submit</button></p>
        </div>
      </Busy>
    </template>
    <template #right>
      <h1>Tokenized text</h1>
      <TokenizationRender :tokenizedText />
      <h1>Manual edition</h1>
      <TextArea
        v-model="manualTokenizedTextProxy"
        style="font-family: 'Courier New', Courier, monospace; font-size: 70%"
      ></TextArea>
      <p>(If you change something here, you won't be able to ask the LLM for adjustments.)</p>
      <p>
        <button
          @click="manualTokenizedText = null"
          :disabled="manualTokenizedText === null"
          title="Forget all manual changes; go back to the last version from the LLM"
        >
          Reset
        </button>
        <!-- @todo Add a button to reformat the JSON -->
        <!-- @todo Save the manual changes to the API -->
      </p>
    </template>
  </ThreeColumns>
</template>

<style scoped>
.user-prompt {
  margin-left: 10%;
  background-color: lightgrey;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 5px;
}

.assistant-prose {
  margin-right: 10%;
  background-color: lightblue;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 5px;
}
</style>
