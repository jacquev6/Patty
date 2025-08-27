<script setup lang="ts">
import { computed } from 'vue'
import { computedAsync } from '@vueuse/core'

import assert from './assert'
import { type AdaptationStrategy, useAuthenticatedClient } from './apiClient'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from './TextArea.vue'
import MarkDown from './MarkDown.vue'
import FixedColumns from './FixedColumns.vue'
import ComboInput from './ComboInput.vue'
import LlmModelSelector from './LlmModelSelector.vue'
import { useApiConstantsStore } from './ApiConstantsStore'
import { match } from 'ts-pattern'

const props = defineProps<{
  availableStrategySettings: AdaptationStrategy['settings'][]
  disabled: boolean
}>()

const client = useAuthenticatedClient()

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
            choice: true,
          },
          exampleComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
          },
          hintComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
          },
          statementComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
            freeTextInput: true,
            multipleChoicesInput: true,
            selectableInput: true,
            swappableInput: true,
            editableTextInput: false,
            splitWordInput: true,
          },
          referenceComponents: {
            text: true,
            whitespace: true,
            arrow: true,
            formatted: true,
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
  if (
    strategy.value.settings.responseSpecification.format === 'json' &&
    strategy.value.settings.responseSpecification.formalism === 'json-schema'
  ) {
    const response = await client.POST('/api/adaptation-llm-response-schema', {
      body: strategy.value.settings.responseSpecification,
    })
    assert(response.data !== undefined)
    return response.data
  } else {
    return null
  }
}, {})

const settingsName = computed({
  get: () => {
    if (strategy.value.settings.name === null) {
      return ''
    } else {
      return strategy.value.settings.name
    }
  },
  set: (value: string) => {
    if (value.trim() === '') {
      strategy.value.settings.name = null
    } else {
      const found = props.availableStrategySettings.find((s) => s.name === value)
      if (found === undefined) {
        strategy.value.settings.name = value
      } else {
        Object.assign(strategy.value.settings, found)
      }
    }
  },
})

const settingsNameSuggestions = computed(() => {
  return props.availableStrategySettings.map((s) => {
    assert(s.name !== null)
    return s.name
  })
})
</script>

<template>
  <h1>Strategy</h1>
  <h2>LLM model</h2>
  <p>
    <LlmModelSelector
      :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
      :disabled
      v-model="strategy.model"
    />
  </p>

  <h2>Settings</h2>
  <p v-if="disabled">Name: {{ settingsName }}</p>
  <p v-else>
    Name:
    <ComboInput
      data-cy="settings-name"
      :suggestions="settingsNameSuggestions"
      :maxSuggestionsDisplayCount="10"
      v-model="settingsName"
    />
  </p>
  <h3>Constraints on LLM's response</h3>
  <p v-if="disabled">LLM response format: {{ llmResponseSpecificationFormalism }}</p>
  <p v-else>
    LLM response format:
    <select v-model="llmResponseSpecificationFormalism">
      <option value="text">text</option>
      <option value="json-object">JSON (without schema)</option>
      <option value="json-schema">JSON schema</option>
    </select>
  </p>
  <template v-if="strategy.settings.responseSpecification.formalism === 'text'">
    <p v-if="!disabled">
      No constraints are placed on the LLM's response. The system prompt <b>must</b> instruct the LLM to respond with
      only a JSON object in its text response. This response format will likely lead to errors when we parse the JSON
      from the LLM's unconstrained text response and when we enforce the JSON schema.
    </p>
  </template>
  <template v-else-if="strategy.settings.responseSpecification.formalism === 'json-object'">
    <p v-if="!disabled">
      This response format ensures the LLM returns proper JSON. According to
      <a href="https://docs.mistral.ai/capabilities/structured-output/json_mode/">the MistralAI documentation</a>, the
      system prompt must still instruct the LLM to respond with a JSON object. This response format may lead to errors
      when we enforce the JSON schema on the LLM's unconstrained JSON response.
    </p>
  </template>
  <template v-else-if="strategy.settings.responseSpecification.formalism === 'json-schema'">
    <p v-if="!disabled">
      This response format ensures the LLM returns a JSON object that respects our schema (<a
        href="https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/"
        >MistralAI documentation</a
      >).
    </p>
    <h4>Allowed components</h4>
    <FixedColumns :columns="[1, 1, 1, 2, 1]">
      <template #col-1>
        <h5>In instruction</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
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
            choice</label
          >
        </p>
      </template>
      <template #col-2>
        <h5>In example</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
          </label>
        </p>
      </template>
      <template #col-3>
        <h5>In hint</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
          </label>
        </p>
      </template>
      <template #col-4>
        <h5>In statement</h5>
        <FixedColumns :columns="[1, 1]" :gutters="false">
          <template #col-1>
            <p style="margin-bottom: 0">
              <label title="text, whitespace, arrow, formatted">
                <input type="checkbox" checked disabled /> text, <i>etc.</i>
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
                free text input
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
                multiple choices input
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
                selectable input
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
                swappable input
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
                editable text input
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
                split word input
              </label>
            </p>
          </template>
        </FixedColumns>
      </template>
      <template #col-5>
        <h5>In reference</h5>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
          </label>
        </p>
      </template>
    </FixedColumns>
    <AdaptedExerciseJsonSchemaDetails v-if="schema !== null" :schema />
  </template>
  <template v-else>
    <p>Unknown response specification: {{ ((f: never) => f)(strategy.settings.responseSpecification) }}</p>
  </template>
  <h3>System prompt</h3>
  <MarkDown v-if="disabled" :markdown="strategy.settings.systemPrompt" />
  <TextArea v-else data-cy="system-prompt" v-model="strategy.settings.systemPrompt"></TextArea>
</template>

<style scoped>
h5 {
  margin: 0;
}
</style>
