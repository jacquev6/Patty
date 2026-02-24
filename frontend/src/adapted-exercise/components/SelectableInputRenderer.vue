<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

import type {
  PassiveRenderable,
  SelectableInputRenderable,
  StudentAnswers,
} from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import assert from '$/assert'

const props = defineProps<{
  path: string
  contents: (PassiveRenderable | SelectableInputRenderable)[]
  colors: string[]
  boxed: boolean
  mayBeSingleLetter: boolean
  tricolorable: boolean
}>()

const studentAnswers = inject<Ref<StudentAnswers>>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const colorIndexProxy = computed<number, number>({
  get() {
    const answer = studentAnswers.value[props.path]
    if (answer === undefined) {
      return 0
    } else {
      assert(answer.kind === 'selectable')
      return answer.color
    }
  },
  set: (color: number) => {
    studentAnswers.value[props.path] = { kind: 'selectable', color }
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
    @click.stop="increment()"
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
