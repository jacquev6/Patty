<script setup lang="ts">
import { computed } from 'vue'

import assert from '@/assert'
import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { InProgressExercise, StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  componentIndex: number
  contents: PassiveRenderable[]
  tricolorable: boolean
}>()

const selected = computed(
  () =>
    inProgress.value.selectedSwappable !== null &&
    inProgress.value.selectedSwappable.pageIndex === props.pageIndex &&
    inProgress.value.selectedSwappable.lineIndex === props.lineIndex &&
    inProgress.value.selectedSwappable.componentIndex === props.componentIndex,
)

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const inProgress = defineModel<InProgressExercise>('inProgress', { required: true })

const contentsFrom = computed(() => {
  const answer = studentAnswers.value.pages[props.pageIndex]?.lines[props.lineIndex]?.components[props.componentIndex]
  if (answer === undefined) {
    return { pageIndex: props.pageIndex, lineIndex: props.lineIndex, componentIndex: props.componentIndex }
  } else {
    assert(answer.kind === 'swappable')
    return answer.contentsFrom
  }
})

const actualContents = computed(() => {
  const { pageIndex, lineIndex, componentIndex } = contentsFrom.value
  const page = inProgress.value.exercise.pages[pageIndex]
  assert(page.kind === 'statement')
  const component = page.statement[lineIndex].contents[componentIndex]
  assert(component.kind === 'swappableInput')
  return component.contents
})

const highlighted = computed(() => (selected.value ? '#FFFDD4' : null))

function setAnswer(
  pageIndex: number,
  lineIndex: number,
  componentIndex: number,
  contentsFrom: {
    pageIndex: number
    lineIndex: number
    componentIndex: number
  },
) {
  studentAnswers.value.pages[pageIndex] ??= { lines: {} }
  studentAnswers.value.pages[pageIndex]!.lines ??= {}
  studentAnswers.value.pages[pageIndex]!.lines[lineIndex] ??= { components: {} }
  studentAnswers.value.pages[pageIndex]!.lines[lineIndex]!.components[componentIndex] = {
    kind: 'swappable',
    contentsFrom,
  }
}

function handleClick() {
  if (inProgress.value.selectedSwappable !== null && inProgress.value.selectedSwappable.pageIndex === props.pageIndex) {
    if (
      inProgress.value.selectedSwappable.lineIndex !== props.lineIndex ||
      inProgress.value.selectedSwappable.componentIndex !== props.componentIndex
    ) {
      const contentsFromBefore = contentsFrom.value
      setAnswer(props.pageIndex, props.lineIndex, props.componentIndex, inProgress.value.selectedSwappable.contentsFrom)
      setAnswer(
        inProgress.value.selectedSwappable.pageIndex,
        inProgress.value.selectedSwappable.lineIndex,
        inProgress.value.selectedSwappable.componentIndex,
        contentsFromBefore,
      )
    }
    inProgress.value.selectedSwappable = null
  } else {
    inProgress.value.selectedSwappable = {
      pageIndex: props.pageIndex,
      lineIndex: props.lineIndex,
      componentIndex: props.componentIndex,
      contentsFrom: contentsFrom.value,
    }
  }
}
</script>

<template>
  <FormattedTextRenderer
    class="main"
    :class="{ empty: actualContents.length === 0 }"
    :contents="actualContents"
    :bold="false"
    :italic="false"
    :underlined="false"
    :boxed="false"
    :superscript="false"
    :subscript="false"
    :highlighted
    :tricolorable
    data-cy="swappableInput"
    @click="handleClick"
  />
</template>

<style scoped>
.main {
  cursor: pointer;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
  border: 2px solid #aaf;
  padding: 9px 3.2px;
}

.main.empty {
  padding: 9px 32px;
}

.main + .main {
  margin-left: 0.26em;
}
</style>
