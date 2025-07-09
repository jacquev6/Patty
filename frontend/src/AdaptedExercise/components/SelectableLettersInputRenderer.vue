<script setup lang="ts">
import { computed, inject, reactive, watch, type Ref } from 'vue'

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

const modelProxy = computed<number[]>({
  get() {
    const answer = studentAnswers[props.path]
    if (answer === undefined) {
      return Array(props.contents.length).fill(0)
    } else {
      assert(answer.kind === 'highlights')
      return answer.highlights
    }
  },
  set(highlights: number[]) {
    studentAnswers[props.path] = { kind: 'highlights', highlights }
  },
})

const highlights: number[] = reactive([])
watch(
  modelProxy,
  () => {
    highlights.splice(0, highlights.length, ...modelProxy.value)
  },
  { immediate: true, deep: true },
)
watch(
  highlights,
  (newHighlights) => {
    modelProxy.value = newHighlights
  },
  { deep: true },
)

const formattedContents = computed((): PassiveRenderable[] => {
  return Array.from(props.contents).map((c, index) => ({
    kind: 'formatted',
    contents: [{ kind: 'text', text: c }],
    highlighted: highlights[index] === 0 ? null : props.colors[highlights[index] - 1],
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
  highlights[index] = (highlights[index] + 1) % (props.colors.length + 1)
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
              :style="{ backgroundColor: colors[highlights[index] - 1] }"
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
