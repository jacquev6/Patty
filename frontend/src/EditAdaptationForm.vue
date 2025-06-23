<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import Ajv, { type ErrorObject } from 'ajv'
import { useMagicKeys } from '@vueuse/core'

import { useAuthenticatedClient, type Adaptation, type AdaptedExercise } from './apiClient'
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
import { type PreprocessedAdaptation } from './adaptations'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import { match } from 'ts-pattern'

const props = defineProps<{
  adaptation: PreprocessedAdaptation
}>()

const emit = defineEmits<{
  (e: 'adaptation-updated', adaptation: Adaptation): void
}>()

const client = useAuthenticatedClient()

const authenticationTokenStore = useAuthenticationTokenStore()

const ajv = new Ajv()
const validateAdaptedExercise = ajv.compile(adaptedExerciseSchema)

type ManualAdaptedExercise = {
  parsed: AdaptedExercise | null
  raw: string
  syntaxError: SyntaxError | null
  validationErrors: ErrorObject[]
}

const manualAdaptedExercise = ref<ManualAdaptedExercise | null>(null)
watch(
  () => props.adaptation,
  (adaptation) => {
    if (adaptation.status.kind === 'success' && adaptation.status.success === 'manual') {
      manualAdaptedExercise.value = {
        parsed: adaptation.status.adaptedExercise,
        raw: jsonStringify(adaptation.status.adaptedExercise),
        syntaxError: null,
        validationErrors: [],
      }
    } else {
      manualAdaptedExercise.value = null
    }
  },
  { immediate: true },
)

const adaptedExercise = computed(() => {
  if (manualAdaptedExercise.value !== null) {
    return manualAdaptedExercise.value.parsed
  } else if (props.adaptation.llmStatus.kind === 'success') {
    return props.adaptation.llmStatus.adaptedExercise
  } else {
    return null
  }
})

const manualAdaptedExerciseProxy = computed({
  get() {
    if (manualAdaptedExercise.value !== null) {
      return manualAdaptedExercise.value.raw
    } else {
      return match(props.adaptation.llmStatus)
        .with({ kind: 'inProgress' }, () => '')
        .with({ kind: 'success' }, (status) => jsonStringify(status.adaptedExercise))
        .with({ kind: 'error', error: 'not-json' }, (status) => status.text)
        .with({ kind: 'error', error: 'invalid-json' }, (status) => jsonStringify(status.parsed))
        .with({ kind: 'error', error: 'unknown' }, () => '')
        .exhaustive()
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
      /* No await: fire and forget */ client.PUT('/api/adaptations/{id}/manual-edit', {
        params: { path: { id: props.adaptation.id } },
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

const syntaxErrorProxy = computed(() => {
  if (manualAdaptedExercise.value !== null) {
    return manualAdaptedExercise.value.syntaxError
  } else if (props.adaptation.llmStatus.kind === 'error' && props.adaptation.llmStatus.error === 'not-json') {
    try {
      JSON.parse(props.adaptation.llmStatus.text)
    } catch (error) {
      if (error instanceof SyntaxError) {
        return error
      } else {
        throw error
      }
    }
    return null
  } else {
    return null
  }
})

const validationErrorsProxy = computed(() => {
  if (manualAdaptedExercise.value !== null) {
    return manualAdaptedExercise.value.validationErrors
  } else if (props.adaptation.llmStatus.kind === 'error' && props.adaptation.llmStatus.error === 'invalid-json') {
    assert(!validateAdaptedExercise(props.adaptation.llmStatus.parsed))
    assert(validateAdaptedExercise.errors !== undefined)
    assert(validateAdaptedExercise.errors !== null)
    return validateAdaptedExercise.errors
  } else {
    return []
  }
})

function reformatManualAdaptedExercise() {
  assert(manualAdaptedExercise.value !== null)
  assert(manualAdaptedExercise.value.parsed !== null)

  manualAdaptedExercise.value.raw = jsonStringify(manualAdaptedExercise.value.parsed)
}

const adjustmentPrompt = ref('')
const isAdjustmentPromptDisabled = computed(() => manualAdaptedExercise.value !== null)
const isSubmitAdjustmentDisabled = computed(
  () => isAdjustmentPromptDisabled.value || adjustmentPrompt.value.trim() === '',
)
const busy = ref(false)

async function submitAdjustment() {
  busy.value = true

  const responsePromise = client.POST(`/api/adaptations/{id}/adjustment`, {
    params: { path: { id: props.adaptation.id } },
    body: { adjustment: adjustmentPrompt.value },
  })

  adjustmentPrompt.value = ''
  const response = await responsePromise

  if (response.data !== undefined) {
    emit('adaptation-updated', response.data)
  }

  busy.value = false
}

async function deleteLastAdjustment() {
  const responsePromise = client.DELETE(`/api/adaptations/{id}/last-adjustment`, {
    params: { path: { id: props.adaptation.id } },
  })

  const response = await responsePromise
  if (response.data !== undefined) {
    emit('adaptation-updated', response.data)
  }
}

function resetManualEdit() {
  manualAdaptedExercise.value = null
  /* No await: fire and forget */ client.DELETE('/api/adaptations/{id}/manual-edit', {
    params: { path: { id: props.adaptation.id } },
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
  <ResizableColumns :columns="[1, 1, 1]">
    <template #col-1>
      <p>
        Created by: {{ adaptation.createdBy
        }}<template v-if="adaptation.classificationBatchId !== null"
          >, part of
          <RouterLink :to="{ name: 'classification-batch', params: { id: adaptation.classificationBatchId } }"
            >this batch</RouterLink
          ></template
        ><template v-if="adaptation.adaptationBatchId !== null"
          >, part of
          <RouterLink :to="{ name: 'adaptation-batch', params: { id: adaptation.adaptationBatchId } }"
            >this batch</RouterLink
          ></template
        >.
      </p>
      <AdaptationStrategyEditor :availableStrategySettings="[]" :disabled="true" :modelValue="adaptation.strategy" />
    </template>
    <template #col-2>
      <h1>Input</h1>
      <p>Page: {{ adaptation.input.pageNumber ?? 'N/A' }}, exercise: {{ adaptation.input.exerciseNumber ?? 'N/A' }}</p>
      <p>
        <template v-for="(line, index) in adaptation.input.text">
          <br v-if="index !== 0" />
          {{ line }}
        </template>
      </p>
      <h1>Adjustments</h1>
      <p><button @click="showRaw = true">View the raw conversation with the LLM</button></p>
      <BusyBox :busy>
        <template v-for="(adjustmentPrompt, adjustmentIndex) in adaptation.adjustmentPrompts">
          <div style="display: flex" class="user-prompt">
            <MarkDown :markdown="adjustmentPrompt" style="flex-grow: 1" />
            <div
              v-if="adjustmentIndex === adaptation.adjustmentPrompts.length - 1"
              title="Rewind the chat: delete this prompt and its effects"
              style="cursor: pointer"
              @click="deleteLastAdjustment"
            >
              ❌
            </div>
          </div>
        </template>
        <div class="user-prompt">
          <TextArea data-cy="user-prompt" v-model="adjustmentPrompt" :disabled="isAdjustmentPromptDisabled"></TextArea>
          <p>
            <button data-cy="submit-adjustment" @click="submitAdjustment" :disabled="isSubmitAdjustmentDisabled">
              Submit
            </button>
          </p>
        </div>
      </BusyBox>
    </template>
    <template #col-3>
      <template v-if="adaptedExercise === null">
        <template v-if="manualAdaptedExercise === null">
          <template v-if="/*assert*/ adaptation.llmStatus.kind === 'error'">
            <h1>Error with the LLM</h1>
            <p>
              <template v-if="adaptation.llmStatus.error === 'invalid-json'">
                The LLM returned a JSON response that does not validate against the adapted exercise schema.
              </template>
              <template v-else-if="adaptation.llmStatus.error === 'not-json'">
                The LLM returned a response that is not correct JSON.
              </template>
              <template v-else-if="adaptation.llmStatus.error === 'unknown'">
                The LLM caused an unknown error.
              </template>
              <template v-else>BUG: {{ ((status: never) => status)(adaptation.llmStatus) }}</template>
              You can:
            </p>
            <ul>
              <li v-if="adaptation.llmStatus.error !== 'unknown'">ask the LLM for an adjustment</li>
              <li v-if="adaptation.llmStatus.error === 'invalid-json'">
                edit the JSON manually to make it conform to the schema
              </li>
              <li v-else-if="adaptation.llmStatus.error === 'not-json'">
                edit the response manually to make it correct JSON that conforms to the schema
              </li>
              <li v-else-if="adaptation.llmStatus.error === 'unknown'">ask Vincent Jacques to investigate</li>
              <li v-else>BUG: {{ ((status: never) => status)(adaptation.llmStatus) }}</li>
            </ul>
          </template>
        </template>
        <template v-else>
          <h1>Error in manually edited exercise</h1>
          <p>
            <template v-if="manualAdaptedExercise.syntaxError !== null">
              The manually edited exercise is not correct JSON.
            </template>
            <template v-else-if="manualAdaptedExercise.validationErrors.length !== 0">
              The manually edited exercise does not validate against the adapted exercise schema.
            </template>
          </p>
        </template>
        <template v-if="syntaxErrorProxy !== null">
          <h2>Syntax error</h2>
          {{ syntaxErrorProxy.message }}
        </template>
        <template v-else-if="validationErrorsProxy.length !== 0">
          <h2>Validation errors</h2>
          <ul>
            <li v-for="error in validationErrorsProxy">
              {{ error.instancePath }}: {{ error.message }}
              {{ Object.keys(error.params).length !== 0 ? JSON.stringify(error.params) : '' }}
            </li>
          </ul>
        </template>
      </template>
      <template v-else>
        <h1>Adapted exercise</h1>
        <MiniatureScreen :fullScreen>
          <AdaptedExerciseRenderer :navigateUsingArrowKeys="fullScreen" :adaptedExercise />
          <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">Exit full screen (Esc)</button>
        </MiniatureScreen>
        <p>
          <button @click="fullScreen = true">Full screen</button>
          <WhiteSpace />
          <a :href="`/api/export/adaptation/${adaptation.id}.html?token=${authenticationTokenStore.token}`">
            Download standalone HTML
          </a>
        </p>
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
