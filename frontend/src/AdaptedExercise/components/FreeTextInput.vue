<script setup lang="ts">
import { computed, onBeforeUpdate, onMounted, useTemplateRef } from 'vue'

import assert from '@/assert'

defineProps<{
  kind: 'freeTextInput'
  tricolorable: boolean
}>()

const model = defineModel<string>({ required: true })

const empty = computed(() => model.value === '')

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

function filterKeyDown(event: KeyboardEvent) {
  if (
    // We don't want new lines in student answers
    event.key === 'Enter' ||
    // Arrows are used to change the page (in 'PageNavigationControls')
    event.key === 'ArrowLeft' ||
    event.key === 'ArrowRight'
  ) {
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
    @keydown="filterKeyDown"
    class="main"
    :class="{ empty, tricolorable }"
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

.main:focus {
  background-color: #fffdd4;
}
</style>
