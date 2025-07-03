<script setup lang="ts">
import { computed, onBeforeUpdate, onMounted, useTemplateRef } from 'vue'

import assert from '@/assert'

const props = defineProps<{
  kind: 'freeTextInput'
  tricolorable: boolean
  aloneOnLine: boolean
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

  let currentNode: Node | null = null
  let currentOffset = 0
  const treeWalker = document.createTreeWalker(span.value, NodeFilter.SHOW_TEXT)
  while ((currentNode = treeWalker.nextNode())) {
    assert(currentNode.nodeValue !== null)
    const nodeLength = currentNode.nodeValue.length
    if (currentOffset + nodeLength >= caretPosition) {
      const sel = document.getSelection()
      assert(sel !== null)
      sel.removeAllRanges()
      const range = document.createRange()
      range.setStart(currentNode, caretPosition - currentOffset)
      range.collapse(true)
      sel.addRange(range)
      break
    }
    currentOffset += nodeLength
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
    :class="{ empty, notAlone: !props.aloneOnLine }"
  ></span>
</template>

<style scoped>
.main {
  line-height: 1em; /* Fix caret position on Chrome */
  padding: 4px;
}

.notAlone {
  border: 2px outset black;
}

.empty {
  padding-left: 1ch;
  padding-right: 1ch;
}

.main:focus {
  outline: 0;
}

.notAlone:focus {
  background-color: #fffdd4;
}
</style>
