<script setup lang="ts">
import { computed, onBeforeUpdate, onMounted, useTemplateRef } from 'vue'

import assert from '@/assert'

const props = defineProps<{
  kind: 'freeTextInput'
  tricolorable: boolean
}>()

const model = defineModel<string>({ required: true })

const empty = computed(() => model.value === '')

const span = useTemplateRef('span')

function input() {
  assert(span.value !== null)
  assert(span.value.textContent !== null)
  model.value = span.value.textContent
}

function getCaretPosition(): number | null {
  assert(span.value !== null)
  const selection = document.getSelection()
  if (selection === null || selection.rangeCount === 0) {
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

  const caretPosition = getCaretPosition()

  if (props.tricolorable) {
    span.value.innerHTML = model.value
      .split(/(\s+)/)
      .map((part) => {
        if (part.trim() === '') {
          return part
        } else {
          return `<span class="tricolorable">${part}</span>`
        }
      })
      .join('')
  } else {
    span.value.textContent = model.value
  }
  assert(span.value.textContent === model.value)

  if (caretPosition !== null) {
    setCaretPosition(caretPosition)
  }
}

onMounted(updateContent)
onBeforeUpdate(updateContent)

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
    @input="input"
    @keydown="filterKeyDown"
    class="main"
    :class="{ empty }"
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
