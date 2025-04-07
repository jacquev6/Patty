<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { type AdaptationInput, type AdaptationStrategy, type LlmModel, client } from './apiClient'
import assert from './assert'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'
import AdaptedExerciseJsonSchemaDetails from './AdaptedExerciseJsonSchemaDetails.vue'
import ResizableColumns from './ResizableColumns.vue'
import { computedAsync } from '@vueuse/core'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  defaultStrategy: AdaptationStrategy
  defaultInput: AdaptationInput
}>()

const router = useRouter()

const availableLlmModels = computed(() => props.availableLlmModels)

assert(availableLlmModels.value.length !== 0)
const llmModel = ref(props.defaultStrategy.model)
watch(
  () => props.defaultStrategy.model,
  (defaultLlmModel) => {
    llmModel.value = defaultLlmModel
  },
)

const llmProviders = computed(() => {
  return [...new Set(availableLlmModels.value.map((model) => model.provider))]
})

const llmProvider = computed({
  get: () => {
    return llmModel.value?.provider ?? ''
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find((model) => model.provider === value)
    assert(model !== undefined)
    llmModel.value = model
  },
})

const llmNames = computed(() => {
  return availableLlmModels.value.filter((model) => model.provider === llmProvider.value).map((model) => model.name)
})

const llmName = computed({
  get: () => {
    return llmModel.value?.name ?? ''
  },
  set: (value: string) => {
    const model = availableLlmModels.value.find(
      (model) => model.provider === llmModel.value?.provider && model.name === value,
    )
    assert(model !== undefined)
    llmModel.value = model
  },
})

const allowChoiceInInstruction = ref(true)
watch(
  () => props.defaultStrategy.allowChoiceInInstruction,
  (defaultAllowChoiceInInstruction) => {
    allowChoiceInInstruction.value = defaultAllowChoiceInInstruction
  },
  { immediate: true },
)

const allowArrowInStatement = ref(true)
watch(
  () => props.defaultStrategy.allowArrowInStatement,
  (defaultAllowArrowInStatement) => {
    allowArrowInStatement.value = defaultAllowArrowInStatement
  },
  { immediate: true },
)
const allowFreeTextInputInStatement = ref(true)
watch(
  () => props.defaultStrategy.allowFreeTextInputInStatement,
  (defaultAllowFreeTextInputInStatement) => {
    allowFreeTextInputInStatement.value = defaultAllowFreeTextInputInStatement
  },
  { immediate: true },
)
const allowMultipleChoicesInputInStatement = ref(true)
watch(
  () => props.defaultStrategy.allowMultipleChoicesInputInStatement,
  (defaultAllowMultipleChoicesInputInStatement) => {
    allowMultipleChoicesInputInStatement.value = defaultAllowMultipleChoicesInputInStatement
  },
  { immediate: true },
)
const allowSelectableInputInStatement = ref(true)
watch(
  () => props.defaultStrategy.allowSelectableInputInStatement,
  (defaultAllowSelectableInputInStatement) => {
    allowSelectableInputInStatement.value = defaultAllowSelectableInputInStatement
  },
  { immediate: true },
)

const schema = computedAsync(async () => {
  const response = await client.GET('/api/adaptation/llm-response-schema', {
    params: {
      query: {
        allow_choice_in_instruction: allowChoiceInInstruction.value,
        allow_arrow_in_statement: allowArrowInStatement.value,
        allow_free_text_input_in_statement: allowFreeTextInputInStatement.value,
        allow_multiple_choices_input_in_statement: allowMultipleChoicesInputInStatement.value,
        allow_selectable_input_in_statement: allowSelectableInputInStatement.value,
      },
    },
  })
  return response.data ?? {}
}, {})

const systemPrompt = ref(props.defaultStrategy.systemPrompt)
watch(
  () => props.defaultStrategy.systemPrompt,
  (defaultSystemPrompt) => {
    systemPrompt.value = defaultSystemPrompt
  },
)

const inputText = ref(props.defaultInput.text)
watch(
  () => props.defaultInput.text,
  (defaultInputText) => {
    inputText.value = defaultInputText
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  assert(llmModel.value !== null)

  const responsePromise = client.POST('/api/adaptation', {
    body: {
      strategy: {
        id: props.defaultStrategy.id,
        model: llmModel.value,
        systemPrompt: systemPrompt.value,
        allowChoiceInInstruction: allowChoiceInInstruction.value,
        allowArrowInStatement: allowArrowInStatement.value,
        allowFreeTextInputInStatement: allowFreeTextInputInStatement.value,
        allowMultipleChoicesInputInStatement: allowMultipleChoicesInputInStatement.value,
        allowSelectableInputInStatement: allowSelectableInputInStatement.value,
      },
      input: { id: props.defaultInput.id, text: inputText.value },
    },
  })

  const response = await responsePromise
  busy.value = false

  if (response.data !== undefined) {
    router.push({ name: 'adaptation', params: { id: response.data.id } })
  }
}

const disabled = computed(() => {
  return systemPrompt.value.trim() === '' || inputText.value.trim() === ''
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <BusyBox :busy>
      <ResizableColumns :columns="2">
        <template #col-1>
          <h1>LLM model</h1>
          <select data-cy="llm-provider" v-model="llmProvider">
            <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option>
          </select>
          <select data-cy="llm-name" v-model="llmName">
            <option v-for="name in llmNames">{{ name }}</option>
          </select>
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
                  ><input data-cy="allow-choice-in-instruction" type="checkbox" v-model="allowChoiceInInstruction" />
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
                      ><input data-cy="allow-arrow-in-statement" type="checkbox" v-model="allowArrowInStatement" />
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
                        v-model="allowFreeTextInputInStatement"
                      />
                      free text input</label
                    >
                  </p>
                  <p>
                    <label
                      ><input
                        data-cy="allow-multiple-choices-input-in-statement"
                        type="checkbox"
                        v-model="allowMultipleChoicesInputInStatement"
                      />
                      multiple choices input</label
                    >
                  </p>
                  <p>
                    <label
                      ><input
                        data-cy="allow-selectable-input-in-statement"
                        type="checkbox"
                        v-model="allowSelectableInputInStatement"
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
          <TextArea data-cy="system-prompt" v-model="systemPrompt"></TextArea>
        </template>
        <template #col-2>
          <h1>Input text</h1>
          <TextArea data-cy="input-text" v-model="inputText"></TextArea>
          <p><button @click="submit" :disabled>Submit</button></p>
        </template>
      </ResizableColumns>
    </BusyBox>
  </div>
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
