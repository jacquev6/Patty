<script setup lang="ts">
import { computed, inject, reactive, ref, watch, type Ref } from 'vue'

import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { ComponentAnswer, PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import assert from '@/assert'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  componentIndex: number
  contents: string
  colors: string[]
  boxed: boolean
  tricolorable: boolean
  getComponentAnswer: () => ComponentAnswer | undefined
  setComponentAnswer: (answer: ComponentAnswer) => void
}>()

const modelProxy = computed<number[]>({
  get() {
    const answer = props.getComponentAnswer()
    if (answer === undefined) {
      return Array(props.contents.length).fill(0)
    } else {
      assert(answer.kind === 'highlights')
      return answer.highlights
    }
  },
  set(highlights: number[]) {
    props.setComponentAnswer({ kind: 'highlights', highlights })
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

const showPicker = ref(false)
watch(
  () => props.pageIndex,
  () => {
    showPicker.value = false
  },
  { immediate: true },
)

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
