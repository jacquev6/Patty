<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, nextTick, onBeforeUpdate, onMounted, useTemplateRef } from 'vue'

import assert from '$/assert'

const props = defineProps<{
  digitsOnly: boolean
}>()

const model = defineModel<string>({ required: true })

const empty = computed(() => model.value === '')
const digits = computed(() => Array.from(model.value).every((c) => '0123456789'.includes(c)))

const span = useTemplateRef('span')

// @todo Consider homogenizing with 'FreeTextInput.vue' (not as easy as it sounds, because of interactions with 'VirtualNumericalKeyboard.vue').

async function input() {
  assert(span.value !== null)
  assert(span.value.textContent !== null)
  let caretPosition = getCaretPosition()

  const filteredText = Array.from(span.value.textContent)
    .filter((c) => !props.digitsOnly || '0123456789'.includes(c))
    .join('')
  if (filteredText !== span.value.textContent && caretPosition !== null) {
    caretPosition -= 1
  }

  model.value = filteredText
  updateContent()

  if (caretPosition !== null) {
    await nextTick()
    setCaretPosition(caretPosition)
  }
}

function getCaretPosition(): number | null {
  assert(span.value !== null)
  const selection = document.getSelection()
  if (selection === null) {
    return null
  }
  const range = selection.getRangeAt(0)
  assert(range.startContainer === range.endContainer)
  assert(range.startOffset === range.endOffset)
  let container = range.startContainer
  let offset = range.startOffset
  while (container !== span.value) {
    let prev = container.previousSibling
    while (prev !== null) {
      if (prev instanceof Text) {
        offset += prev.length
      } else if (prev instanceof HTMLElement) {
        assert(prev.textContent !== null)
        offset += prev.textContent.length
      } else {
        return null
      }
      prev = prev.previousSibling
    }
    const parent = container.parentElement
    if (parent === null) {
      return null
    } else {
      container = parent
    }
  }
  return offset
}

function setCaretPosition(caretPosition: number) {
  assert(span.value !== null)
  let index = 0
  let length = 0
  while (length < caretPosition) {
    const child = span.value.childNodes[index]
    if (child instanceof Text) {
      length += child.length
    } else if (child instanceof HTMLElement) {
      assert(child.textContent !== null)
      length += child.textContent.length
    } else {
      return
    }
    index += 1
  }
  const selection = document.getSelection()
  if (selection !== null) {
    const range = document.createRange()
    range.setStart(span.value, index)
    range.setEnd(span.value, index)
    selection.removeAllRanges()
    selection.addRange(range)
  }
}

function updateContent() {
  assert(span.value !== null)
  span.value.childNodes.forEach((child) => child.remove())
  span.value.innerHTML = Array.from(model.value)
    .map((c) => `<span>${c}</span>`)
    .join('')
}

onMounted(updateContent)
onBeforeUpdate(updateContent) // For re-used components

function filterKeyDown(event: KeyboardEvent) {
  if (
    // Forbid new lines
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
    contenteditable
    @input="input"
    @keydown="filterKeyDown"
    class="main"
    :class="{ empty, digits }"
  ></span>
</template>

<style scoped>
.main {
  line-height: 1em; /* Fix caret position on Chrome */
  padding: 4px;
  border: 2px outset black;
}

.main.empty {
  padding-left: 1ch;
  padding-right: 1ch;
}

.main:focus {
  background-color: #fffdd4;
}

.main.digits > :deep(span:nth-last-child(3n + 1)) {
  color: #00f;
}

.main.digits > :deep(span:nth-last-child(3n + 2)) {
  color: #f00;
}

.main.digits > :deep(span:nth-last-child(3n + 3)) {
  color: #0c0;
}
</style>
