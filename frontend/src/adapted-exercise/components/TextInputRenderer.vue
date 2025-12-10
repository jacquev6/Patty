<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, inject, onBeforeUpdate, onMounted, useTemplateRef, type Ref } from 'vue'

import assert from '$/assert'
import type { StudentAnswers } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'

const props = defineProps<{
  path: string
  initialText: string
  increaseHorizontalSpace: boolean
  tricolorable: boolean
  aloneOnLine: boolean
}>()

const studentAnswers = inject<Ref<StudentAnswers>>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const modelProxy = computed<string>({
  get() {
    const answer = studentAnswers.value[props.path]
    if (answer === undefined) {
      return props.initialText
    } else {
      assert(answer.kind === 'text')
      return answer.text
    }
  },
  set(value: string) {
    studentAnswers.value[props.path] = { kind: 'text', text: value }
  },
})

const empty = computed(() => modelProxy.value === '')

const span = useTemplateRef('span')

function input() {
  assert(span.value !== null)
  assert(span.value.textContent !== null)
  modelProxy.value = span.value.textContent
  updateContent()
}

function getCaretPosition(): number | null {
  assert(span.value !== null)
  const selection = document.getSelection()
  if (selection === null || selection.rangeCount === 0) {
    return null
  }
  const range = selection.getRangeAt(0)
  if (span.value.contains(range.startContainer)) {
    range.setStart(span.value, 0)
    return range.toString().length
  } else {
    return null
  }
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
    span.value.innerHTML = modelProxy.value
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
    span.value.textContent = modelProxy.value
  }
  assert(span.value.textContent === modelProxy.value)

  if (caretPosition !== null) {
    setCaretPosition(caretPosition)
  }
}

onMounted(updateContent)
onBeforeUpdate(updateContent)

function onKeyDown(event: KeyboardEvent) {
  assert(span.value !== null)
  if (event.key === 'Escape') {
    span.value.blur()
  }
}

function focus() {
  assert(span.value !== null)
  span.value.focus()
}

defineExpose({
  focus,
})
</script>

<template>
  <span
    ref="span"
    data-cy="freeTextInput"
    contenteditable
    @input="input"
    @keydown.stop="onKeyDown"
    class="main"
    :class="{ empty, notAlone: !props.aloneOnLine, increaseHorizontalSpace }"
  ></span>
</template>

<style scoped>
.main {
  line-height: 1em; /* Fix caret position on Chrome */
  padding: 4px;
}

.increaseHorizontalSpace {
  padding-left: calc(4px + var(--optional-extra-horizontal-space-between-letters-in-editable-text-input));
  letter-spacing: var(--optional-extra-horizontal-space-between-letters-in-editable-text-input);
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
