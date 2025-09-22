<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import jsonStringify from 'json-stringify-pretty-compact'
import Ajv, { type ErrorObject } from 'ajv'
import { useMagicKeys } from '@vueuse/core'
import { match } from 'ts-pattern'

import { useAuthenticatedClient, type Adaptation, type AdaptedExercise } from '@/frontend/ApiClient'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import ResizableColumns from '$/ResizableColumns.vue'
import TextArea from '$/TextArea.vue'
import assert from '$/assert'
import MarkDown from '$/MarkDown.vue'
import BusyBox from '$/BusyBox.vue'
import adaptedExerciseSchema from '@/../../backend/generated/adapted-exercise-schema.json'
import MiniatureScreen from '$/MiniatureScreen.vue'
import WhiteSpace from '$/WhiteSpace.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'

const props = defineProps<{
  adaptation: Adaptation
}>()

const emit = defineEmits<{
  (e: 'adaptation-updated'): void
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()

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
  await responsePromise

  emit('adaptation-updated')

  busy.value = false
}

async function deleteLastAdjustment() {
  await client.DELETE(`/api/adaptations/{id}/last-adjustment`, {
    params: { path: { id: props.adaptation.id } },
  })

  emit('adaptation-updated')
}

async function resetManualEdit() {
  manualAdaptedExercise.value = null
  await client.DELETE('/api/adaptations/{id}/manual-edit', {
    params: { path: { id: props.adaptation.id } },
  })

  emit('adaptation-updated')
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
      <AdaptationStrategyEditor :availableStrategySettings="[]" :disabled="true" :modelValue="adaptation.strategy" />
    </template>
    <template #col-2>
      <h1>{{ t('input') }}</h1>
      <p>
        {{ t('page') }}: {{ adaptation.input.pageNumber ?? t('na') }}, {{ t('exercise') }}:
        {{ adaptation.input.exerciseNumber ?? t('na') }}
      </p>
      <p>
        <template v-for="(line, index) in adaptation.input.text">
          <br v-if="index !== 0" />
          {{ line }}
        </template>
      </p>
      <h1>{{ t('adjustments') }}</h1>
      <p>
        <button @click="showRaw = true">{{ t('viewRaw') }}</button>
      </p>
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
              {{ t('submit') }}
            </button>
          </p>
        </div>
      </BusyBox>
    </template>
    <template #col-3>
      <template v-if="adaptedExercise === null">
        <template v-if="manualAdaptedExercise === null">
          <template v-if="/*assert*/ adaptation.llmStatus.kind === 'error'">
            <h1>{{ t('llmError') }}</h1>
            <p>
              <template v-if="adaptation.llmStatus.error === 'invalid-json'">
                {{ t('llmInvalidJson') }}
              </template>
              <template v-else-if="adaptation.llmStatus.error === 'not-json'">
                {{ t('llmNotJson') }}
              </template>
              <template v-else-if="adaptation.llmStatus.error === 'unknown'">
                {{ t('llmUnknownError') }}
              </template>
              <template v-else>BUG: {{ ((status: never) => status)(adaptation.llmStatus) }}</template>
              {{ t('youCan') }}
            </p>
            <ul>
              <li v-if="adaptation.llmStatus.error !== 'unknown'">{{ t('askAdjustment') }}</li>
              <li v-if="adaptation.llmStatus.error === 'invalid-json'">{{ t('editJson') }}</li>
              <li v-else-if="adaptation.llmStatus.error === 'not-json'">{{ t('editResponse') }}</li>
              <li v-else-if="adaptation.llmStatus.error === 'unknown'">{{ t('askVincent') }}</li>
              <li v-else>BUG: {{ ((status: never) => status)(adaptation.llmStatus) }}</li>
            </ul>
          </template>
        </template>
        <template v-else>
          <h1>{{ t('manualEditError') }}</h1>
          <p>
            <template v-if="manualAdaptedExercise.syntaxError !== null">
              {{ t('manualNotJson') }}
            </template>
            <template v-else-if="manualAdaptedExercise.validationErrors.length !== 0">
              {{ t('manualInvalidJson') }}
            </template>
          </p>
        </template>
        <template v-if="syntaxErrorProxy !== null">
          <h2>{{ t('syntaxError') }}</h2>
          {{ syntaxErrorProxy.message }}
        </template>
        <template v-else-if="validationErrorsProxy.length !== 0">
          <h2>{{ t('validationErrors') }}</h2>
          <ul>
            <li v-for="error in validationErrorsProxy">
              {{ error.instancePath }}: {{ error.message }}
              {{ Object.keys(error.params).length !== 0 ? JSON.stringify(error.params) : '' }}
            </li>
          </ul>
        </template>
      </template>
      <template v-else>
        <h1>{{ t('adaptedExercise') }}</h1>
        <MiniatureScreen :fullScreen>
          <AdaptedExerciseRenderer
            :navigateUsingArrowKeys="fullScreen"
            :adaptedExercise
            :imagesUrls="adaptation.imagesUrls"
          />
          <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">
            {{ t('exitFullScreen') }}
          </button>
        </MiniatureScreen>
        <p>
          <button @click="fullScreen = true">{{ t('fullScreen') }}</button>
          <WhiteSpace />
          <a :href="`/api/export/adaptation/${adaptation.id}.html?token=${authenticationTokenStore.token}`">
            {{ t('downloadHtml') }}
          </a>
        </p>
      </template>
      <h1>{{ t('manualEdition') }}</h1>
      <TextArea
        data-cy="manual-edition"
        v-model="manualAdaptedExerciseProxy"
        style="font-family: 'Courier New', Courier, monospace; font-size: 70%"
      ></TextArea>
      <p>{{ t('manualEditionWarning') }}</p>
      <p>
        <button
          data-cy="reset-manual-edition"
          @click="resetManualEdit"
          :disabled="manualAdaptedExercise === null"
          title="Forget all manual changes; go back to the last version from the LLM"
        >
          {{ t('reset') }}
        </button>
        <WhiteSpace />
        <button
          data-cy="reformat-manual-edition"
          @click="reformatManualAdaptedExercise"
          :disabled="manualAdaptedExercise === null || manualAdaptedExercise.parsed === null"
        >
          {{ t('reformat') }}
        </button>
      </p>
    </template>
  </ResizableColumns>
  <div v-if="showRaw" class="overlay">
    <div>
      <div>
        <h1>{{ t('rawConversation') }}</h1>
        <button class="exitFullScreen" @click="showRaw = false">{{ t('close') }}</button>
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

<i18n>
en:
  input: Input
  page: Page
  exercise: exercise
  na: N/A
  submit: Submit
  adjustments: Adjustments
  viewRaw: View the raw conversation with the LLM
  llmError: Error with the LLM
  llmInvalidJson: The LLM returned a JSON response that does not validate against the adapted exercise schema.
  llmNotJson: The LLM returned a response that is not correct JSON.
  llmUnknownError: The LLM caused an unknown error.
  youCan: "You can:"
  askAdjustment: ask the LLM for an adjustment
  editJson: edit the JSON manually to make it conform to the schema
  editResponse: edit the response manually to make it correct JSON that conforms to the schema
  askVincent: ask Vincent Jacques to investigate
  manualEditError: Error in manually edited exercise
  manualNotJson: The manually edited exercise is not correct JSON.
  manualInvalidJson: The manually edited exercise does not validate against the adapted exercise schema.
  syntaxError: Syntax error
  validationErrors: Validation errors
  adaptedExercise: Adapted exercise
  exitFullScreen: Exit full screen (Esc)
  fullScreen: Full screen
  downloadHtml: Download standalone HTML
  manualEdition: Manual edition
  manualEditionWarning: (If you change something here, you won't be able to ask the LLM for adjustments.)
  reset: Reset
  reformat: Reformat
  rawConversation: Raw conversation with the LLM
  close: Close (Esc)
fr:
  input: Entrée
  page: Page
  exercise: exercice
  na: N/D
  submit: Soumettre
  adjustments: Ajustements
  viewRaw: Voir la conversation brute avec le LLM
  llmError: Erreur avec le LLM
  llmInvalidJson: Le LLM a retourné une réponse JSON qui ne valide pas contre le schéma d'exercice adapté.
  llmNotJson: Le LLM a retourné une réponse qui n'est pas un JSON correct.
  llmUnknownError: Le LLM a causé une erreur inconnue.
  youCan: "Vous pouvez :"
  askAdjustment: demander un ajustement au LLM
  editJson: éditer le JSON manuellement pour le rendre conforme au schéma
  editResponse: éditer la réponse manuellement pour qu'elle soit un JSON correct conforme au schéma
  askVincent: demander à Vincent Jacques d'enquêter
  manualEditError: Erreur dans l'exercice édité manuellement
  manualNotJson: L'exercice édité manuellement n'est pas un JSON correct.
  manualInvalidJson: L'exercice édité manuellement ne valide pas contre le schéma d'exercice adapté.
  syntaxError: Erreur de syntaxe
  validationErrors: Erreurs de validation
  adaptedExercise: Exercice adapté
  exitFullScreen: Quitter le plein écran (Échap)
  fullScreen: Plein écran
  downloadHtml: Télécharger le HTML autonome
  manualEdition: Édition manuelle
  manualEditionWarning: (Si vous modifiez quelque chose ici, vous ne pourrez plus demander d'ajustements au LLM.)
  reset: Réinitialiser
  reformat: Reformater
  rawConversation: Conversation brute avec le LLM
  close: Fermer (Échap)
</i18n>
