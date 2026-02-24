<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script lang="ts">
import { type AdaptationStrategy } from '../ApiClient'

export function makeAdaptationSettingsName(identity: AdaptationStrategy['settings']['identity']): string {
  if (identity === null) {
    return ''
  } else {
    return identity.name + (identity.version !== 'current' ? ` (${identity.version} version)` : '')
  }
}
</script>

<script setup lang="ts">
import { computed } from 'vue'
import { computedAsync } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import assert from '$/assert'
import { useAuthenticatedClient } from '../ApiClient'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from '$/TextArea.vue'
import MarkDown from '$/MarkDown.vue'
import FixedColumns from '$/FixedColumns.vue'
import ComboInput from '$/ComboInput.vue'
import LlmModelSelector from './LlmModelSelector.vue'
import { useApiConstantsStore } from '../ApiConstantsStore'
import { match } from 'ts-pattern'

const props = defineProps<{
  availableStrategySettings: AdaptationStrategy['settings'][]
  disabled: boolean
}>()

const client = useAuthenticatedClient()
const { t } = useI18n()

const apiConstantsStore = useApiConstantsStore()

const strategy = defineModel<AdaptationStrategy>({ required: true })

const llmResponseSpecificationFormalism = computed({
  get: () => {
    return strategy.value.settings.responseSpecification.formalism
  },
  set: (value: typeof strategy.value.settings.responseSpecification.formalism) => {
    match(value)
      .with('json-object', () => {
        strategy.value.settings.responseSpecification = { format: 'json', formalism: 'json-object' }
      })
      .with('json-schema', () => {
        strategy.value.settings.responseSpecification = {
          format: 'json',
          formalism: 'json-schema',
          instructionComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            image: true,
            choice: true,
          },
          exampleComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            image: true,
          },
          hintComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            image: true,
          },
          statementComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            image: true,
            freeTextInput: true,
            multipleChoicesInput: true,
            selectableInput: true,
            swappableInput: true,
            editableTextInput: true,
            splitWordInput: true,
          },
          referenceComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            image: true,
          },
        }
      })
      .with('text', () => {
        strategy.value.settings.responseSpecification = { format: 'json', formalism: 'text' }
      })
      .exhaustive()
  },
})

const schema = computedAsync(async () => {
  const response = await client.POST('/api/adaptation-llm-response-schema', {
    body: strategy.value.settings.responseSpecification,
  })
  assert(response.data !== undefined)
  return response.data
}, {})

const settingsName = computed({
  get: () => {
    if (strategy.value.settings.identity === null) {
      return ''
    } else {
      return makeAdaptationSettingsName(strategy.value.settings.identity)
    }
  },
  set: (value: string) => {
    if (value.trim() === '') {
      strategy.value.settings.identity = null
    } else {
      const found = props.availableStrategySettings.find((s) => makeAdaptationSettingsName(s.identity) === value)
      if (found === undefined) {
        strategy.value.settings.identity = { name: value, version: 'current' }
      } else {
        Object.assign(strategy.value.settings, found)
      }
    }
  },
})

const settingsNameSuggestions = computed(() => {
  return props.availableStrategySettings.map((s) => {
    assert(s.identity !== null)
    return makeAdaptationSettingsName(s.identity)
  })
})

const textFormalismIsDisabled = computed(() => {
  return !apiConstantsStore.formalismIsAvailableForAdaptationLlmModel(strategy.value.model, 'text')
})

const jsonObjectFormalismIsDisabled = computed(() => {
  return !apiConstantsStore.formalismIsAvailableForAdaptationLlmModel(strategy.value.model, 'json-object')
})

const jsonSchemaFormalismIsDisabled = computed(() => {
  return !apiConstantsStore.formalismIsAvailableForAdaptationLlmModel(strategy.value.model, 'json-schema')
})
</script>

<template>
  <h1>{{ t('strategy') }}</h1>
  <h2>{{ t('llmModel') }}</h2>
  <p>
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
      :disabled
      v-model="strategy.model"
    />
  </p>

  <h2>{{ t('settings') }}</h2>
  <p v-if="disabled">{{ t('name') }}: {{ settingsName }}</p>
  <p v-else>
    {{ t('name') }}:
    <ComboInput
      data-cy="settings-name"
      :suggestions="settingsNameSuggestions"
      :maxSuggestionsDisplayCount="10"
      v-model="settingsName"
    />
  </p>
  <h3>{{ t('constraints') }}</h3>
  <p v-if="disabled">{{ t('llmResponseFormat') }}: {{ llmResponseSpecificationFormalism }}</p>
  <p v-else>
    {{ t('llmResponseFormat') }}:
    <select v-model="llmResponseSpecificationFormalism">
      <option value="text" :disabled="textFormalismIsDisabled">{{ t('text') }}</option>
      <option value="json-object" :disabled="jsonObjectFormalismIsDisabled">{{ t('jsonNoSchema') }}</option>
      <option value="json-schema" :disabled="jsonSchemaFormalismIsDisabled">{{ t('jsonSchema') }}</option>
    </select>
  </p>
  <template v-if="strategy.settings.responseSpecification.formalism === 'text'">
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-v-html -->
    <p v-if="!disabled" v-html="t('textFormalismDescription')"></p>
  </template>
  <template v-else-if="strategy.settings.responseSpecification.formalism === 'json-object'">
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-v-html -->
    <p v-if="!disabled" v-html="t('jsonObjectFormalismDescription')"></p>
  </template>
  <template v-else-if="strategy.settings.responseSpecification.formalism === 'json-schema'">
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-v-html -->
    <p v-if="!disabled" v-html="t('jsonSchemaFormalismDescription')"></p>
    <h4>{{ t('allowedComponents') }}</h4>
    <FixedColumns :columns="[1, 1, 1, 2, 1]">
      <template #col-1>
        <h5>{{ t('inInstruction') }}</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> {{ t('text') }}, <i>{{ t('etc') }}</i>
          </label>
        </p>
        <p>
          <label
            ><input
              data-cy="allow-choice-in-instruction"
              type="checkbox"
              v-model="strategy.settings.responseSpecification.instructionComponents.choice"
              :disabled
            />
            {{ t('choice') }}</label
          >
        </p>
      </template>
      <template #col-2>
        <h5>{{ t('inExample') }}</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> {{ t('text') }}, <i>{{ t('etc') }}</i>
          </label>
        </p>
      </template>
      <template #col-3>
        <h5>{{ t('inHint') }}</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> {{ t('text') }}, <i>{{ t('etc') }}</i>
          </label>
        </p>
      </template>
      <template #col-4>
        <h5>{{ t('inStatement') }}</h5>
        <FixedColumns :columns="[1, 1]" :gutters="false">
          <template #col-1>
            <p style="margin-bottom: 0">
              <label title="text, whitespace, arrow, formatted">
                <input type="checkbox" checked disabled /> {{ t('text') }}, <i>{{ t('etc') }}</i>
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-free-text-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.freeTextInput"
                  :disabled
                />
                {{ t('freeTextInput') }}
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-multiple-choices-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.multipleChoicesInput"
                  :disabled
                />
                {{ t('multipleChoicesInput') }}
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-selectable-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.selectableInput"
                  :disabled
                />
                {{ t('selectableInput') }}
              </label>
            </p>
          </template>
          <template #col-2>
            <p>
              <label>
                <input
                  data-cy="allow-swappable-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.swappableInput"
                  :disabled
                />
                {{ t('swappableInput') }}
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-editable-text-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.editableTextInput"
                  :disabled
                />
                {{ t('editableTextInput') }}
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-split-word-input-in-statement"
                  type="checkbox"
                  v-model="strategy.settings.responseSpecification.statementComponents.splitWordInput"
                  :disabled
                />
                {{ t('splitWordInput') }}
              </label>
            </p>
          </template>
        </FixedColumns>
      </template>
      <template #col-5>
        <h5>{{ t('inReference') }}</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> {{ t('text') }}, <i>{{ t('etc') }}</i>
          </label>
        </p>
      </template>
    </FixedColumns>
  </template>
  <template v-else>
    <p>{{ t('unknownResponseSpec') }}: {{ ((f: never) => f)(strategy.settings.responseSpecification) }}</p>
  </template>
  <AdaptedExerciseJsonSchemaDetails v-if="schema !== null" :schema />
  <h3>{{ t('systemPrompt') }}</h3>
  <MarkDown v-if="disabled" :markdown="strategy.settings.systemPrompt" />
  <TextArea v-else data-cy="system-prompt" v-model="strategy.settings.systemPrompt"></TextArea>
</template>

<style scoped>
h5 {
  margin: 0;
}
</style>

<i18n>
en:
  strategy: Strategy
  llmModel: LLM model
  settings: Settings
  name: Name
  constraints: Constraints on LLM's response
  llmResponseFormat: LLM response format
  text: text
  jsonNoSchema: JSON (without schema)
  jsonSchema: JSON schema
  textFormalismDescription: "No constraints are placed on the LLM's response. The system prompt <b>must</b> instruct the LLM to respond with only a JSON object in its text response. This response format will likely lead to errors when we parse the JSON from the LLM's unconstrained text response and when we enforce the JSON schema."
  jsonObjectFormalismDescription: "This response format ensures the LLM returns proper JSON. According to <a href=\"https://docs.mistral.ai/capabilities/structured-output/json_mode/\">the MistralAI documentation</a>, the system prompt must still instruct the LLM to respond with a JSON object. This response format may lead to errors when we enforce the JSON schema on the LLM's unconstrained JSON response."
  jsonSchemaFormalismDescription: "This response format ensures the LLM returns a JSON object that respects our schema (<a href=\"https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/\">MistralAI documentation</a>)."
  allowedComponents: Allowed components
  inInstruction: In instruction
  choice: choice
  etc: etc.
  inExample: In example
  inHint: In hint
  inStatement: In statement
  freeTextInput: free text input
  multipleChoicesInput: multiple choices input
  selectableInput: selectable input
  swappableInput: swappable input
  editableTextInput: editable text input
  splitWordInput: split word input
  inReference: In reference
  unknownResponseSpec: Unknown response specification
  systemPrompt: System prompt
fr:
  strategy: Stratégie
  llmModel: Modèle LLM
  settings: Paramètres
  name: Nom
  constraints: Contraintes sur la réponse du LLM
  llmResponseFormat: Format de réponse du LLM
  text: texte
  jsonNoSchema: JSON (sans schéma)
  jsonSchema: Schéma JSON
  textFormalismDescription: "Aucune contrainte n'est imposée à la réponse du LLM. Le prompt système <b>doit</b> indiquer au LLM de répondre uniquement avec un objet JSON dans sa réponse textuelle. Ce format de réponse entraînera probablement des erreurs lorsque nous extrairons le JSON à partir de la réponse textuelle non contrainte du LLM et lorsque nous appliquerons le schéma JSON."
  jsonObjectFormalismDescription: "Ce format de réponse garantit que le LLM renvoie du JSON. D'après la <a href=\"https://docs.mistral.ai/capabilities/structured-output/json_mode/\">documentation de MistralAI</a>, le prompt système doit quand même indiquer au LLM de répondre avec un objet JSON. Ce format de réponse peut entraîner des erreurs lorsque nous appliquons le schéma JSON à la réponse du LLM."
  jsonSchemaFormalismDescription: "Ce format de réponse garantit que le LLM renvoie un objet JSON qui respecte notre schéma (<a href=\"https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/\">documentation MistralAI</a>)."
  allowedComponents: Composants autorisés
  inInstruction: Dans la consigne
  choice: choix
  etc: etc.
  inExample: Dans l'exemple
  inHint: Dans l'indice
  inStatement: Dans l'énoncé
  freeTextInput: champs texte libre
  multipleChoicesInput: champs à choix multiples
  selectableInput: champs sélectionnable
  swappableInput: champs permutable
  editableTextInput: champs de texte éditable
  splitWordInput: champs de mot à découper
  inReference: Dans la référence
  unknownResponseSpec: Spécification de réponse inconnue
  systemPrompt: Prompt système
</i18n>
