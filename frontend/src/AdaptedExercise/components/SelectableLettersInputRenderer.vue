<script setup lang="ts">
import { computed, inject, reactive, ref, watch, type Ref } from 'vue'

import FormattedTextRenderer from './FormattedTextRenderer.vue'
import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import assert from '@/assert'

const props = defineProps<{
  contents: string
  colors: string[]
  boxed: boolean
  tricolorable: boolean
}>()

const highlights: number[] = reactive([])
watch(
  () => props.contents,
  () => {
    highlights.splice(0, highlights.length, ...Array(props.contents.length).fill(0))
  },
  { immediate: true },
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

function increment(index: number) {
  console.log('increment', index, highlights[index])
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
          </div>
          <div>
            <p><span style="cursor: pointer" @click="showPicker = false">✅</span></p>
          </div>
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
