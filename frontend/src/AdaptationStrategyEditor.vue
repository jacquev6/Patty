<script setup lang="ts">
import { computed } from 'vue'
import { computedAsync } from '@vueuse/core'

import assert from './assert'
import { type AdaptationStrategy, type LlmModel, client } from './apiClient'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import TextArea from './TextArea.vue'
import MarkDown from './MarkDown.vue'

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

const schema = computedAsync(async () => {
  const response = await client.GET('/api/adaptation/llm-response-schema', {
    params: {
      query: {
        allow_choice_in_instruction: strategy.value.allowChoiceInInstruction,
        allow_arrow_in_statement: strategy.value.allowArrowInStatement,
        allow_free_text_input_in_statement: strategy.value.allowFreeTextInputInStatement,
        allow_multiple_choices_input_in_statement: strategy.value.allowMultipleChoicesInputInStatement,
        allow_selectable_input_in_statement: strategy.value.allowSelectableInputInStatement,
      },
    },
  })
  return response.data ?? {}
}, {})
</script>

<template>
  <h1>LLM model</h1>
  <p v-if="disabled">{{ strategy.model.provider }}: {{ strategy.model.name }}</p>
  <p v-else>
    <select data-cy="llm-provider" v-model="llmProvider">
      <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option>
    </select>
    <select data-cy="llm-name" v-model="llmName">
      <option v-for="name in llmNames">{{ name }}</option>
    </select>
  </p>

  <h1>Allowed components in LLM's response</h1>
  <div style="display: grid; grid-template-columns: 1fr 11px 2fr 11px 1fr">
    <div>
      <h2>In instruction</h2>
      <p>
        <label><input type="checkbox" checked disabled /> text</label>
      </p>
      <p>
        <label><input type="checkbox" checked disabled /> whitespace</label>
      </p>
      <p>
        <label
          ><input
            data-cy="allow-choice-in-instruction"
            type="checkbox"
            v-model="strategy.allowChoiceInInstruction"
            :disabled
          />
          choice</label
        >
      </p>
    </div>
    <div class="gutter"></div>
    <div>
      <h2>In statement</h2>
      <div style="display: grid; grid-template-columns: 1fr 1fr">
        <div>
          <p>
            <label><input type="checkbox" checked disabled /> text</label>
          </p>
          <p>
            <label><input type="checkbox" checked disabled /> whitespace</label>
          </p>
          <p>
            <label
              ><input
                data-cy="allow-arrow-in-statement"
                type="checkbox"
                v-model="strategy.allowArrowInStatement"
                :disabled
              />
              arrow</label
            >
          </p>
        </div>
        <div>
          <p>
            <label
              ><input
                data-cy="allow-free-text-input-in-statement"
                type="checkbox"
                v-model="strategy.allowFreeTextInputInStatement"
                :disabled
              />
              free text input</label
            >
          </p>
          <p>
            <label
              ><input
                data-cy="allow-multiple-choices-input-in-statement"
                type="checkbox"
                v-model="strategy.allowMultipleChoicesInputInStatement"
                :disabled
              />
              multiple choices input</label
            >
          </p>
          <p>
            <label
              ><input
                data-cy="allow-selectable-input-in-statement"
                type="checkbox"
                v-model="strategy.allowSelectableInputInStatement"
                :disabled
              />
              selectable input</label
            >
          </p>
        </div>
      </div>
    </div>
    <div class="gutter"></div>
    <div>
      <h2>In references</h2>
      <p>
        <label><input type="checkbox" checked disabled /> text</label>
      </p>
      <p>
        <label><input type="checkbox" checked disabled /> whitespace</label>
      </p>
    </div>
  </div>
  <AdaptedExerciseJsonSchemaDetails :schema />
  <h1>System prompt</h1>
  <MarkDown v-if="disabled" :markdown="strategy.systemPrompt" />
  <TextArea v-else data-cy="system-prompt" v-model="strategy.systemPrompt"></TextArea>
</template>

<style scoped>
.gutter {
  background-color: black;
  margin: 0 5px;
}

h2 {
  margin: 0;
}
</style>
