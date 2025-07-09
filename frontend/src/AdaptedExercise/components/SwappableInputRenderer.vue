<script setup lang="ts">
import { computed, inject } from 'vue'

import assert from '@/assert'
import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { InProgressExercise, StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  path: string
  pageIndex: number
  lineIndex: number
  componentIndex: number
  contents: PassiveRenderable[]
  tricolorable: boolean
}>()

const studentAnswers = inject<StudentAnswers>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const inProgress = inject<InProgressExercise>('adaptedExerciseInProgress')
assert(inProgress !== undefined)

const selected = computed(
  () =>
    inProgress.p.kind === 'movingSwappable' &&
    inProgress.p.swappable.pageIndex === props.pageIndex &&
    inProgress.p.swappable.lineIndex === props.lineIndex &&
    inProgress.p.swappable.componentIndex === props.componentIndex,
)

const contentsFrom = computed(() => {
  const answer = studentAnswers[props.path]
  if (answer === undefined) {
    return { pageIndex: props.pageIndex, lineIndex: props.lineIndex, componentIndex: props.componentIndex }
  } else {
    assert(answer.kind === 'swappable')
    return answer.contentsFrom
  }
})

const actualContents = computed(() => {
  const { pageIndex, lineIndex, componentIndex } = contentsFrom.value
  const page = inProgress.exercise.pages[pageIndex]
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
  assert(studentAnswers !== undefined)
  const path = `stmt-pg${pageIndex}-ln${lineIndex}-ct${componentIndex}` // @todo Deduplicate this path construction logic.
  studentAnswers[path] = { kind: 'swappable', contentsFrom }
}

function handleClick() {
  assert(inProgress !== undefined)
  if (inProgress.p.kind === 'movingSwappable' && inProgress.p.swappable.pageIndex === props.pageIndex) {
    if (
      inProgress.p.swappable.lineIndex !== props.lineIndex ||
      inProgress.p.swappable.componentIndex !== props.componentIndex
    ) {
      const contentsFromBefore = contentsFrom.value
      setAnswer(props.pageIndex, props.lineIndex, props.componentIndex, inProgress.p.swappable.contentsFrom)
      setAnswer(
        inProgress.p.swappable.pageIndex,
        inProgress.p.swappable.lineIndex,
        inProgress.p.swappable.componentIndex,
        contentsFromBefore,
      )
    }
    inProgress.p = { kind: 'none' }
  } else {
    inProgress.p = {
      kind: 'movingSwappable',
      swappable: {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        contentsFrom: contentsFrom.value,
      },
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
