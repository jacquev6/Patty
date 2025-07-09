<script setup lang="ts">
import { computed, inject } from 'vue'

import assert from '@/assert'
import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { InProgressExercise, StudentAnswers } from '../AdaptedExerciseRenderer.vue'

const props = defineProps<{
  path: string
  contents: PassiveRenderable[]
  tricolorable: boolean
}>()

const studentAnswers = inject<StudentAnswers>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const inProgress = inject<InProgressExercise>('adaptedExerciseInProgress')
assert(inProgress !== undefined)

const selected = computed(() => inProgress.p.kind === 'movingSwappable' && inProgress.p.swappable.path === props.path)

const contentsFrom = computed(() => {
  const answer = studentAnswers[props.path]
  if (answer === undefined) {
    return props.path
  } else {
    assert(answer.kind === 'swappable')
    return answer.contentsFrom
  }
})

const actualContents = computed(() => {
  return inProgress.swappables[contentsFrom.value].contents
})

const highlighted = computed(() => (selected.value ? '#FFFDD4' : null))

function setAnswer(path: string, contentsFrom: string) {
  assert(studentAnswers !== undefined)
  studentAnswers[path] = { kind: 'swappable', contentsFrom }
}

function handleClick() {
  assert(inProgress !== undefined)
  if (inProgress.p.kind === 'movingSwappable') {
    if (inProgress.p.swappable.path !== props.path) {
      const contentsFromBefore = contentsFrom.value
      setAnswer(props.path, inProgress.p.swappable.contentsFrom)
      setAnswer(inProgress.p.swappable.path, contentsFromBefore)
    }
    inProgress.p = { kind: 'none' }
  } else {
    inProgress.p = {
      kind: 'movingSwappable',
      swappable: {
        path: props.path,
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
