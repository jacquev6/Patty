<script setup lang="ts">
import { computed, inject } from 'vue'

import type { PassiveRenderable, StudentAnswers } from '../AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import assert from '@/assert'

const props = defineProps<{
  path: string
  contents: PassiveRenderable[]
  colors: string[]
  boxed: boolean
  mayBeSingleLetter: boolean
  tricolorable: boolean
}>()

const studentAnswers = inject<StudentAnswers>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const colorIndexProxy = computed<number, number>({
  get() {
    const answer = studentAnswers[props.path]
    if (answer === undefined) {
      return 0
    } else {
      assert(answer.kind === 'selectable')
      return answer.color
    }
  },
  set: (color: number) => {
    studentAnswers[props.path] = { kind: 'selectable', color }
  },
})

function increment() {
  colorIndexProxy.value = (colorIndexProxy.value + 1) % (props.colors.length + 1)
}

const highlighted = computed(() => (colorIndexProxy.value === 0 ? null : props.colors[colorIndexProxy.value - 1]))

const single = computed(() => {
  if (props.contents.length === 1 && props.contents[0].kind === 'text' && props.contents[0].text.length === 1) {
    const c = props.contents[0].text[0]
    if ('.!?,;:'.includes(c)) {
      return 'punctuation'
    } else {
      return props.mayBeSingleLetter ? 'letter' : null
    }
  } else {
    return null
  }
})
</script>

<template>
  <FormattedTextRenderer
    class="main"
    :class="{
      'single-letter': single === 'letter',
      'single-punctuation': single === 'punctuation',
    }"
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

.single-letter {
  padding: var(--extra-vertical-space-around-single-letter-selectable)
    var(--extra-horizontal-space-around-single-letter-selectable) !important;
  font-size: var(--font-size-for-single-character-selectable);
}

.single-punctuation {
  padding: var(--extra-vertical-space-around-single-punctuation-selectable)
    var(--extra-horizontal-space-around-single-punctuation-selectable) !important;
  font-size: var(--font-size-for-single-character-selectable);
}
</style>
