<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef, watch } from 'vue'
import deepCopy from 'deep-copy'

import { type LatestBatch, type LlmModel } from './apiClient'
import TextArea from './TextArea.vue'
import BusyBox from './BusyBox.vue'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import WhiteSpace from './WhiteSpace.vue'
import assert from './assert'

const props = defineProps<{
  availableLlmModels: LlmModel[]
  latestBatch: LatestBatch
}>()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.latestBatch.strategy))
const inputs = reactive(deepCopy(props.latestBatch.inputs))
watch(
  () => props.latestBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

const textAreas = useTemplateRef<InstanceType<typeof TextArea>[]>('textAreas')

const emptyInputProxy = computed({
  get() {
    return ''
  },
  set(text) {
    inputs.push({ id: 1, createdBy: identifiedUser.identifier, text })
  },
})

const inputProxies = computed(() => [
  ...inputs.map((input) =>
    computed({
      get() {
        return input.text
      },
      set(value) {
        input.text = value
        let popped = false
        while (inputs.length > 0 && inputs[inputs.length - 1].text === '') {
          inputs.pop()
          popped = true
        }
        if (popped) {
          assert(textAreas.value !== null)
          textAreas.value[inputs.length].wrapped.focus()
        }
      },
    }),
  ),
  emptyInputProxy,
])

const busy = ref(false)

async function submit() {}

const cleanedUpInputs = computed(() =>
  inputs
    .map((input) => ({
      ...input,
      text: input.text.trim(),
    }))
    .filter((input) => input.text !== ''),
)

const disabled = computed(() => {
  return strategy.systemPrompt.trim() === '' || cleanedUpInputs.value.length === 0
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <BusyBox :busy>
      <ResizableColumns :columns="[1, 1]">
        <template #col-1>
          <p>Created by: <IdentifiedUser /></p>
          <AdaptationStrategyEditor :availableLlmModels v-model="strategy" />
        </template>
        <template #col-2>
          <h1>Inputs</h1>
          <p><button @click="submit" :disabled>Submit</button></p>
          <template v-for="index in inputs.length + 1">
            <h2>
              Input {{ index
              }}<template v-if="inputProxies[index - 1].value.trim() === ''"
                ><WhiteSpace /><span class="ignored">(empty, ignored)</span></template
              >
            </h2>
            <TextArea
              ref="textAreas"
              id="input-text"
              data-cy="input-text"
              v-model="inputProxies[index - 1].value"
            ></TextArea>
          </template>
        </template>
      </ResizableColumns>
    </BusyBox>
  </div>
</template>

<style scoped>
.ignored {
  font-size: 70%;
  color: grey;
}
</style>
