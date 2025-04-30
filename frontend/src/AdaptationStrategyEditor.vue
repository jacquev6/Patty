<script setup lang="ts">
import { computed } from 'vue'
import { computedAsync } from '@vueuse/core'

import assert from './assert'
import { type AdaptationStrategy, type LlmModel, client } from './apiClient'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from './TextArea.vue'
import MarkDown from './MarkDown.vue'
import FixedColumns from './FixedColumns.vue'

const props = withDefaults(
  defineProps<{
    availableLlmModels: LlmModel[]
    disabled?: boolean
  }>(),
  { disabled: false },
)

const strategy = defineModel<AdaptationStrategy>({ required: true })

const availableLlmModels = computed(() => props.availableLlmModels)

assert(props.disabled || availableLlmModels.value.length !== 0)

const llmProviders = computed(() => {
  return [...new Set(availableLlmModels.value.map((model) => model.provider))]
})

const llmProvider = computed({
  get: () => {
    return strategy.value.model.provider
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find((model) => model.provider === value)
    assert(model !== undefined)
    strategy.value.model = model
  },
})

const llmNames = computed(() => {
  return availableLlmModels.value.filter((model) => model.provider === llmProvider.value).map((model) => model.name)
})

const llmName = computed({
  get: () => {
    return strategy.value.model.name
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find(
      (model) => model.provider === strategy.value.model.provider && model.name === value,
    )
    assert(model !== undefined)
    strategy.value.model = model
  },
})

const llmResponseSpecificationFormalism = computed({
  get: () => {
    return strategy.value.responseSpecification.formalism
  },
  set: (value: typeof strategy.value.responseSpecification.formalism) => {
    if (value === 'json-object') {
      strategy.value.responseSpecification = { format: 'json', formalism: 'json-object' }
    } else if (value === 'json-schema') {
      strategy.value.responseSpecification = {
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
        },
        referenceComponents: {
          text: true,
          whitespace: true,
          arrow: true,
          formatted: true,
        },
      }
    } else if (value === 'text') {
      strategy.value.responseSpecification = { format: 'json', formalism: 'text' }
    } else {
      ;((v: never) => console.log(`Unknown response specification formalism: ${v}`))(value)
    }
  },
})

const schema = computedAsync(async () => {
  if (
    strategy.value.responseSpecification.format === 'json' &&
    strategy.value.responseSpecification.formalism === 'json-schema'
  ) {
    const response = await client.POST('/api/adaptation/llm-response-schema', {
      body: strategy.value.responseSpecification,
    })
    assert(response.data !== undefined)
    return response.data
  } else {
    return null
  }
}, {})
</script>

<template>
  <h1>LLM model</h1>
  <p v-if="disabled">Provider: {{ strategy.model.provider }}, model: {{ strategy.model.name }}</p>
  <p v-else>
    Provider:
    <select data-cy="llm-provider" v-model="llmProvider">
      <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option></select
    >, model:
    <select data-cy="llm-name" v-model="llmName">
      <option v-for="name in llmNames">{{ name }}</option>
    </select>
  </p>

  <h1>Constraints on LLM's response</h1>
  <p v-if="disabled">LLM response format: {{ llmResponseSpecificationFormalism }}</p>
  <p v-else>
    LLM response format:
    <select v-model="llmResponseSpecificationFormalism">
      <option value="text">text</option>
      <option value="json-object">JSON (without schema)</option>
      <option value="json-schema">JSON schema</option>
    </select>
  </p>
  <template v-if="strategy.responseSpecification.formalism === 'text'">
    <p v-if="!disabled">
      No constraints are placed on the LLM's response. The system prompt <b>must</b> instruct the LLM to respond with
      only a JSON object in its text response. This response format will likely lead to errors when we parse the JSON
      from the LLM's unconstrained text response and when we enforce the JSON schema.
    </p>
  </template>
  <template v-else-if="strategy.responseSpecification.formalism === 'json-object'">
    <p v-if="!disabled">
      This response format ensures the LLM returns proper JSON. According to
      <a href="https://docs.mistral.ai/capabilities/structured-output/json_mode/">the MistralAI documentation</a>, the
      system prompt must still instruct the LLM to respond with a JSON object. This response format may lead to errors
      when we enforce the JSON schema on the LLM's unconstrained JSON response.
    </p>
  </template>
  <template v-else-if="strategy.responseSpecification.formalism === 'json-schema'">
    <p v-if="!disabled">
      This response format ensures the LLM returns a JSON object that respects our schema (<a
        href="https://docs.mistral.ai/capabilities/structured-output/custom_structured_output/"
        >MistralAI documentation</a
      >).
    </p>
    <h2>Allowed components</h2>
    <FixedColumns :columns="[1, 1, 1, 2, 1]">
      <template #col-1>
        <h3>In instruction</h3>
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
              v-model="strategy.responseSpecification.instructionComponents.choice"
              :disabled
            />
            choice</label
          >
        </p>
      </template>
      <template #col-2>
        <h3>In example</h3>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
          </label>
        </p>
      </template>
      <template #col-3>
        <h3>In hint</h3>
        <p>
          <label title="text, whitespace, arrow, formatted">
            <input type="checkbox" checked disabled /> text, <i>etc.</i>
          </label>
        </p>
      </template>
      <template #col-4>
        <h3>In statement</h3>
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
                  v-model="strategy.responseSpecification.statementComponents.freeTextInput"
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
                  v-model="strategy.responseSpecification.statementComponents.multipleChoicesInput"
                  :disabled
                />
                multiple choices input
              </label>
            </p>
          </template>
          <template #col-2>
            <p>
              <label>
                <input
                  data-cy="allow-selectable-input-in-statement"
                  type="checkbox"
                  v-model="strategy.responseSpecification.statementComponents.selectableInput"
                  :disabled
                />
                selectable input
              </label>
            </p>
            <p>
              <label>
                <input
                  data-cy="allow-swappable-input-in-statement"
                  type="checkbox"
                  v-model="strategy.responseSpecification.statementComponents.swappableInput"
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
                  v-model="strategy.responseSpecification.statementComponents.editableTextInput"
                  :disabled
                />
                editable text input
              </label>
            </p>
          </template>
        </FixedColumns>
      </template>
      <template #col-5>
        <h3>In reference</h3>
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
    <p>Unknown response specification: {{ ((f: never) => f)(strategy.responseSpecification) }}</p>
  </template>
  <h1>System prompt</h1>
  <MarkDown v-if="disabled" :markdown="strategy.systemPrompt" />
  <TextArea v-else data-cy="system-prompt" v-model="strategy.systemPrompt"></TextArea>
</template>

<style scoped>
h3 {
  margin: 0;
}
</style>
