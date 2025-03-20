<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { onMounted, onBeforeUpdate } from 'vue'

import assert from '@/assert'

defineProps<{
  kind: 'freeTextInput'
  tricolorable: boolean
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
    class="main"
    :class="{ empty: model === '', tricolorable }"
  ></span>
</template>

<style scoped>
.main {
  line-height: 1em; /* Fix caret position on Chrome */
  padding: 4px;
  border: 2px outset black;
}

.empty {
  padding-left: 1ch;
  padding-right: 1ch;
}

.main:hover {
  background-color: #fffdd4;
}
</style>
