<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import Ajv, { type ErrorObject } from 'ajv'
import { useMagicKeys } from '@vueuse/core'

import { client, type Adaptation, type AdaptedExercise } from './apiClient'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import ResizableColumns from './ResizableColumns.vue'
import TextArea from './TextArea.vue'
import assert from './assert'
import MarkDown from './MarkDown.vue'
import BusyBox from './BusyBox.vue'
import adaptedExerciseSchema from '../../backend/generated/adapted-exercise-schema.json'
import MiniatureScreen from './MiniatureScreen.vue'
import WhiteSpace from './WhiteSpace.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'

const props = defineProps<{
  id: string
}>()

const ajv = new Ajv()
const validateAdaptedExercise = ajv.compile(adaptedExerciseSchema)

const found = ref<boolean | null>(null)
const adaptation = ref<Adaptation | null>(null)

onMounted(async () => {
  const response = await client.GET(`/api/adaptation/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    adaptation.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    adaptation.value = response.data
  }
})

const inputText = computed(() => {
  if (adaptation.value === null) {
    return ''
  } else {
    return adaptation.value.input.text
  }
})

const llmError = computed(() => {
  if (adaptation.value === null) {
    return null
  } else {
    if (adaptation.value.adjustments.length === 0) {
      return adaptation.value.initialAssistantError
    } else {
      const lastAdjustment = adaptation.value.adjustments[adaptation.value.adjustments.length - 1]
      return lastAdjustment.assistantError
    }
  }
})

const llmAdaptedExercise = computed(() => {
  if (adaptation.value === null) {
    return null
  } else {
    if (adaptation.value.manualEdit === null) {
      if (adaptation.value.adjustments.length === 0) {
        return adaptation.value.initialAssistantResponse
      } else {
        const lastAdjustment = adaptation.value.adjustments[adaptation.value.adjustments.length - 1]
        return lastAdjustment.assistantResponse
      }
    } else {
      return adaptation.value.manualEdit
    }
  }
})

type ManualAdaptedExercise = {
  parsed: AdaptedExercise | null
  raw: string
  syntaxError: SyntaxError | null
  validationErrors: ErrorObject[]
}

const manualAdaptedExercise = ref<ManualAdaptedExercise | null>(null)
watch(
  adaptation,
  (adaptation) => {
    if (adaptation === null || adaptation.manualEdit === null) {
      manualAdaptedExercise.value = null
    } else {
      manualAdaptedExercise.value = {
        parsed: adaptation.manualEdit,
        raw: jsonStringify(adaptation.manualEdit),
        syntaxError: null,
        validationErrors: [],
      }
    }
  },
  { immediate: true },
)

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
      /* No await: fire and forget */ client.PUT('/api/adaptation/{id}/manual-edit', {
        params: { path: { id: props.id } },
        body: parsed,
      })
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

async function submitAdjustment() {
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

function resetManualEdit() {
  manualAdaptedExercise.value = null
  /* No await: fire and forget */ client.DELETE('/api/adaptation/{id}/manual-edit', {
    params: { path: { id: props.id } },
  })
}

const fullScreen = ref(false)

const showRaw = ref(false)

const { Escape } = useMagicKeys()

watch(Escape, () => {
  showRaw.value = false
  fullScreen.value = false
})
</script>

<template>
  <div v-if="adaptation !== null">
    <ResizableColumns :columns="[1, 1, 1]">
      <template #col-1>
        <p>Created by: {{ adaptation.createdBy }}</p>
        <AdaptationStrategyEditor :availableLlmModels="[]" :disabled="true" v-model="adaptation.strategy" />
      </template>
      <template #col-2>
        <h1>Input text</h1>
        <MarkDown :markdown="inputText" />
        <h1>Adjustments</h1>
        <p><button @click="showRaw = true">View the raw conversation with the LLM</button></p>
        <BusyBox :busy>
          <template v-for="(step, stepIndex) in adaptation.adjustments">
            <div style="display: flex" class="user-prompt">
              <MarkDown :markdown="step.userPrompt" style="flex-grow: 1" />
              <!-- @todo Add a button letting the user display the adaptation returned during that step (only if an adaptation was returned) -->
              <div
                v-if="stepIndex === adaptation.adjustments.length - 1"
                title="Rewind the chat: delete this prompt and its effects"
                style="cursor: pointer"
                @click="rewindLastStep"
              >
                ❌
              </div>
            </div>
          </template>
          <div v-if="llmError === null && manualAdaptedExercise === null" class="user-prompt">
            <TextArea data-cy="user-prompt" v-model="adjustment"></TextArea>
            <p><button data-cy="submit-adjustment" @click="submitAdjustment" :disabled>Submit</button></p>
          </div>
        </BusyBox>
      </template>
      <template #col-3>
        <template v-if="llmError !== null">
          <h1>Error with the LLM</h1>
          <p>
            {{ llmError }}. See the raw conversation to investigate (and/or give the URL of this page to Vincent
            Jacques).
          </p>
        </template>
        <template v-if="llmAdaptedExercise !== null">
          <h1>Adapted exercise</h1>
          <template v-if="adaptedExercise !== null">
            <MiniatureScreen :fullScreen>
              <AdaptedExerciseRenderer :adaptedExercise />
              <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">
                Exit full screen (Esc)
              </button>
            </MiniatureScreen>
            <p>
              <button @click="fullScreen = true">Full screen</button>
              <WhiteSpace />
              <a :href="`/api/adaptation/export/${adaptation.id}.html`">Download standalone HTML</a>
            </p>
          </template>
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
            data-cy="manual-edition"
            v-model="manualAdaptedExerciseProxy"
            style="font-family: 'Courier New', Courier, monospace; font-size: 70%"
          ></TextArea>
          <p>(If you change something here, you won't be able to ask the LLM for adjustments.)</p>
          <p>
            <button
              data-cy="reset-manual-edition"
              @click="resetManualEdit"
              :disabled="manualAdaptedExercise === null"
              title="Forget all manual changes; go back to the last version from the LLM"
            >
              Reset
            </button>
            <WhiteSpace />
            <button
              data-cy="reformat-manual-edition"
              @click="reformatManualAdaptedExercise"
              :disabled="manualAdaptedExercise === null || manualAdaptedExercise.parsed === null"
            >
              Reformat
            </button>
          </p>
        </template>
      </template>
    </ResizableColumns>
    <div v-if="showRaw" class="overlay">
      <div>
        <div>
          <h1>Raw conversation with the LLM</h1>
          <button class="exitFullScreen" @click="showRaw = false">Close (Esc)</button>
          <pre>{{ jsonStringify(adaptation.rawLlmConversations, { maxLength: 120 }) }}</pre>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="found === false">
    <h1>Not found</h1>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}

.overlay > div {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90vw;
  height: 90vh;
  background-color: white;
  padding: 1rem;
  border-radius: 5px;
  box-shadow: 0 0 10px black;
}
.overlay > div > div {
  height: 100%;
  overflow: scroll;
}

.user-prompt {
  background-color: lightblue;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 5px;
}

button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
