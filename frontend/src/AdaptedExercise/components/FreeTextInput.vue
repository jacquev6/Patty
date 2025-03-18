<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { onMounted, onBeforeUpdate } from 'vue'

import assert from '@/assert'

defineProps<{
  kind: 'freeTextInput'
}>()

const model = defineModel<string>({ default: '' })

const span = useTemplateRef('span')

function updateModel() {
  assert(span.value !== null)
  model.value = span.value.innerText
}

function updateContent() {
  assert(span.value !== null)
  const innerText = model.value ?? ''
  // Avoid resetting the caret to the beginning in Firefox: change only if necessary
  if (span.value.innerText !== innerText) {
    span.value.innerText = innerText
  }
}

onMounted(updateContent)
onBeforeUpdate(updateContent) // For re-used components

function forbidNewlines(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
  }
}
</script>

<template>
  <span
    ref="span"
    data-cy="freeTextInput"
    contenteditable
    @input="updateModel"
    @keypress="forbidNewlines"
    :class="{ empty: model === '' }"
  ></span>
</template>

<style scoped>
.empty {
  padding-left: 5px;
  padding-right: 5px;
}
</style>
