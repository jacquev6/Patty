<script setup lang="ts">
import { computed, inject } from 'vue'

import type { ComponentAnswer, PassiveRenderable, StudentAnswers } from '../AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import assert from '@/assert'

const props = defineProps<{
  contents: PassiveRenderable[]
  colors: string[]
  boxed: boolean
  tricolorable: boolean
  getComponentAnswer: (studentAnswers: StudentAnswers) => ComponentAnswer | undefined
  setComponentAnswer: (studentAnswers: StudentAnswers, answer: ComponentAnswer) => void
}>()

const studentAnswers = inject<StudentAnswers>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const colorIndexProxy = computed<number, number>({
  get() {
    const answer = props.getComponentAnswer(studentAnswers)
    if (answer === undefined) {
      return 0
    } else {
      assert(answer.kind === 'selectable')
      return answer.color
    }
  },
  set: (color: number) => {
    props.setComponentAnswer(studentAnswers, { kind: 'selectable', color })
  },
})

function increment() {
  colorIndexProxy.value = (colorIndexProxy.value + 1) % (props.colors.length + 1)
}

const highlighted = computed(() => (colorIndexProxy.value === 0 ? null : props.colors[colorIndexProxy.value - 1]))

const style = computed(() => {
  if (props.contents.length === 1 && props.contents[0].kind === 'text' && props.contents[0].text.length === 1) {
    const c = props.contents[0].text[0]
    if ('.!?,;:'.includes(c)) {
      return {
        padding: '16px 3.2px',
      }
    } else {
      return {
        padding: '2px 2px',
      }
    }
  } else {
    return {}
  }
})
</script>

<template>
  <FormattedTextRenderer
    class="main"
    :style
    :contents
    :bold="false"
    :italic="false"
    :underlined="false"
    :boxed
    :superscript="false"
    :subscript="false"
    :highlighted
    :tricolorable
    data-cy="selectableInput"
    @click="increment()"
  />
</template>

<style scoped>
.main {
  cursor: pointer;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
}

.main:hover {
  outline: 1px dashed green;
}
</style>
