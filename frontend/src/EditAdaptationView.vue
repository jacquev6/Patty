<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import Ajv, { type ErrorObject } from 'ajv'

import { client, type Adaptation } from './apiClient'
import AdaptationRender from './AdaptationRender.vue'
import ThreeColumns from './ThreeColumns.vue'
import TextArea from './TextArea.vue'
import assert from './assert'
import MarkDown from './MarkDown.vue'
import Busy from './BusyBox.vue'
import adaptedExerciseSchema from '../../backend/adapted-exercise-schema.json'

const props = defineProps<{
  id: string
}>()

const ajv = new Ajv()
const validateAdaptedExercise = ajv.compile(adaptedExerciseSchema)

const adaptation = ref<Adaptation | null>(null)

onMounted(async () => {
  const response = await client.GET(`/api/adaptation/{id}`, { params: { path: { id: props.id } } })

  if (response.data !== undefined) {
    adaptation.value = response.data
  }
})

const systemPrompt = computed(() => {
  if (adaptation.value === null) {
    return ''
  } else {
    assert(adaptation.value.steps.length > 0)
    assert(adaptation.value.steps[0].kind === 'initial')
    return adaptation.value.steps[0].system_prompt
  }
})

const inputText = computed(() => {
  if (adaptation.value === null) {
    return ''
  } else {
    assert(adaptation.value.steps.length > 0)
    assert(adaptation.value.steps[0].kind === 'initial')
    return adaptation.value.steps[0].input_text
  }
})

type AdaptedExercise = Adaptation['steps'][number]['adapted_exercise']

const llmAdaptedExercise = computed(() => {
  if (adaptation.value === null) {
    return null
  } else {
    assert(adaptation.value.steps.length > 0)
    return adaptation.value.steps.map((step) => step.adapted_exercise).reduce((old, now) => now ?? old) ?? null
  }
})

type ManualAdaptedExercise = {
  parsed: AdaptedExercise | null
  raw: string
  syntaxError: SyntaxError | null
  validationErrors: ErrorObject[]
}

const manualAdaptedExercise = ref<ManualAdaptedExercise | null>(null)

const adaptedExercise = computed(() => {
  if (manualAdaptedExercise.value !== null) {
    return manualAdaptedExercise.value.parsed
  } else {
    return llmAdaptedExercise.value
  }
})

const manualAdaptedExerciseProxy = computed({
  get() {
    if (manualAdaptedExercise.value === null) {
      return jsonStringify(llmAdaptedExercise.value)
    } else {
      return manualAdaptedExercise.value.raw
    }
  },
  set(raw: string) {
    let parsed: AdaptedExercise | null = null
    try {
      parsed = JSON.parse(raw)
    } catch (syntaxError) {
      if (syntaxError instanceof SyntaxError) {
        manualAdaptedExercise.value = { raw, parsed: null, syntaxError, validationErrors: [] }
        return
      } else {
        throw syntaxError
      }
    }
    assert(parsed !== null)
    if (validateAdaptedExercise(parsed)) {
      manualAdaptedExercise.value = { raw, parsed, syntaxError: null, validationErrors: [] }
    } else {
      assert(validateAdaptedExercise.errors !== undefined)
      assert(validateAdaptedExercise.errors !== null)
      manualAdaptedExercise.value = {
        raw,
        parsed: null,
        syntaxError: null,
        validationErrors: validateAdaptedExercise.errors,
      }
    }
  },
})

function reformatManualAdaptedExercise() {
  assert(manualAdaptedExercise.value !== null)
  assert(manualAdaptedExercise.value.parsed !== null)

  manualAdaptedExercise.value.raw = jsonStringify(manualAdaptedExercise.value.parsed)
}

const adjustment = ref('')
const disabled = computed(() => adjustment.value.trim() === '' || manualAdaptedExercise.value !== null)
const busy = ref(false)

async function submit() {
  busy.value = true

  const responsePromise = client.POST(`/api/adaptation/{id}/adjustment`, {
    params: { path: { id: props.id } },
    body: { adjustment: adjustment.value },
  })

  adjustment.value = ''
  const response = await responsePromise

  if (response.data !== undefined) {
    adaptation.value = response.data
  }

  busy.value = false
}

async function rewindLastStep() {
  const responsePromise = client.DELETE(`/api/adaptation/{id}/last-step`, {
    params: { path: { id: props.id } },
  })

  const response = await responsePromise
  if (response.data !== undefined) {
    adaptation.value = response.data
  }
}
</script>

<template>
  <ThreeColumns v-if="adaptation !== null">
    <template #left>
      <h1>LLM model</h1>
      <p>{{ adaptation.llm_model.provider }}: {{ adaptation.llm_model.name }}</p>
      <h1>System prompt</h1>
      <MarkDown :markdown="systemPrompt" />
    </template>
    <template #center>
      <!-- @todo Offer to display the low level messages exchanged with the LLM -->
      <h1>Input text</h1>
      <MarkDown :markdown="inputText" />
      <h1>Adjustments</h1>
      <Busy :busy>
        <template v-for="(step, stepIndex) in adaptation.steps">
          <div v-if="step.kind === 'adjustment'" style="display: flex" class="user-prompt">
            <MarkDown :markdown="step.user_prompt" style="flex-grow: 1" />
            <!-- @todo Add a button letting the user display the adaptation returned during that step (only if an adaptation was returned) -->
            <div
              v-if="stepIndex === adaptation.steps.length - 1"
              title="Rewind the chat: delete this prompt and its effects"
              style="cursor: pointer"
              @click="rewindLastStep"
            >
              ❌
            </div>
          </div>
          <MarkDown class="assistant-prose" :markdown="step.assistant_prose" />
        </template>
        <div v-if="manualAdaptedExercise === null" class="user-prompt">
          <TextArea v-model="adjustment"></TextArea>
          <p><button @click="submit" :disabled>Submit</button></p>
        </div>
      </Busy>
    </template>
    <template #right>
      <h1>Adapted exercise</h1>
      <AdaptationRender v-if="adaptedExercise !== null" :adaptedExercise />
      <template v-else-if="manualAdaptedExercise !== null">
        <template v-if="manualAdaptedExercise.syntaxError !== null">
          <h2>Syntax error</h2>
          {{ manualAdaptedExercise?.syntaxError.message }}
        </template>
        <template v-else>
          <h2>Validation errors</h2>
          <ul>
            <li v-for="error in manualAdaptedExercise.validationErrors">
              {{ error.instancePath }}: {{ error.message }}
              {{ Object.keys(error.params).length !== 0 ? JSON.stringify(error.params) : '' }}
            </li>
          </ul>
        </template>
      </template>
      <h1>Manual edition</h1>
      <TextArea
        v-model="manualAdaptedExerciseProxy"
        style="font-family: 'Courier New', Courier, monospace; font-size: 70%"
      ></TextArea>
      <p>(If you change something here, you won't be able to ask the LLM for adjustments.)</p>
      <p>
        <button
          @click="manualAdaptedExercise = null"
          :disabled="manualAdaptedExercise === null"
          title="Forget all manual changes; go back to the last version from the LLM"
        >
          Reset
        </button>
        <button
          @click="reformatManualAdaptedExercise"
          :disabled="manualAdaptedExercise === null || manualAdaptedExercise.parsed === null"
        >
          Reformat
        </button>
        <!-- @todo Save the manual changes to the API -->
      </p>
    </template>
  </ThreeColumns>
</template>

<style scoped>
.user-prompt {
  margin-left: 10%;
  background-color: lightblue;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 5px;
}

.assistant-prose {
  margin-right: 10%;
  background-color: lightgrey;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 5px;
}
</style>
