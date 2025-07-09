<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { InProgressExercise, PassiveRenderable, StudentAnswers } from '../AdaptedExerciseRenderer.vue'
import assert from '@/assert'

const props = defineProps<{
  path: string
  contents: string
  colors: string[]
  boxed: boolean
  tricolorable: boolean
}>()

const studentAnswers = inject<StudentAnswers>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const inProgress = inject<InProgressExercise>('adaptedExerciseInProgress')
assert(inProgress !== undefined)

function getHighlighted(index: number): string | null {
  assert(studentAnswers !== undefined)

  const path = `${props.path}-lt${index}`
  if (studentAnswers[path] === undefined) {
    return null
  } else {
    assert(studentAnswers[path].kind === 'selectable')
    const colorIndex = studentAnswers[path].color
    if (colorIndex === 0) {
      return null
    } else {
      return props.colors[colorIndex - 1]
    }
  }
}

function getHighlightedStyle(index: number) {
  const highlighted = getHighlighted(index)
  if (highlighted === null) {
    return {}
  } else {
    return { backgroundColor: highlighted }
  }
}

const formattedContents = computed((): PassiveRenderable[] => {
  return Array.from(props.contents).map((c, index) => ({
    kind: 'formatted',
    contents: [{ kind: 'text', text: c }],
    highlighted: getHighlighted(index),
    bold: false,
    italic: false,
    underlined: false,
    boxed: false,
    superscript: false,
    subscript: false,
  }))
})

const teleportPickerTo = inject<Ref<HTMLDivElement> | null>('adaptedExerciseStatementDiv')
assert(teleportPickerTo !== undefined)

const showPicker = computed({
  get() {
    return inProgress.p.kind === 'solvingSelectableLetters' && inProgress.p.path === props.path
  },
  set(value: boolean) {
    if (value) {
      inProgress.p = {
        kind: 'solvingSelectableLetters',
        path: props.path,
      }
    } else {
      inProgress.p = { kind: 'none' }
    }
  },
})

function increment(index: number) {
  assert(studentAnswers !== undefined)
  const path = `${props.path}-lt${index}`
  if (studentAnswers[path] === undefined) {
    studentAnswers[path] = { kind: 'selectable', color: 0 }
  }
  assert(studentAnswers[path].kind === 'selectable')
  studentAnswers[path].color = (studentAnswers[path].color + 1) % (props.colors.length + 1)
}
</script>

<template>
  <FormattedTextRenderer
    class="main"
    :contents="formattedContents"
    :bold="false"
    :italic="false"
    :underlined="false"
    :boxed
    :superscript="false"
    :subscript="false"
    :highlighted="null"
    :tricolorable
    data-cy="selectableInput"
    @click="showPicker = true"
  />
  <template v-if="showPicker">
    <Teleport :to="teleportPickerTo">
      <div class="picker">
        <div>
          <p>
            <span
              class="letter"
              v-for="(letter, index) in contents"
              @click="increment(index)"
              :style="getHighlightedStyle(index)"
            >
              {{ letter }}
            </span>
          </p>
          <p><span style="cursor: pointer" @click="showPicker = false">✅</span></p>
        </div>
      </div>
    </Teleport>
  </template>
</template>

<style scoped>
.main {
  cursor: pointer;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
}

.main:hover {
  outline: 1px dashed green;
}

.picker {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.picker > div {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  background-color: white;
  font-size: 1.5em;
  text-align: center;
  user-select: none;
}

.letter {
  cursor: pointer;
  padding-left: 0.1em;
  padding-right: 0.1em;
}

.letter:hover {
  outline: 1px dashed green;
}
</style>
