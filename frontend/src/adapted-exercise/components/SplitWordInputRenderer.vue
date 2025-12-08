<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

import assert from '$/assert'
import type { StudentAnswers } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'

const props = defineProps<{
  path: string
  word: string
  tricolorable: boolean
}>()

const separator = '|'

const studentAnswers = inject<Ref<StudentAnswers>>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const letters = computed(() => props.word.split(''))

const separatorIndex = computed({
  get() {
    const answer = studentAnswers.value[props.path]
    if (answer && answer.kind === 'splitWord') {
      return answer.separatorIndex
    }
    return null
  },
  set(index) {
    studentAnswers.value[props.path] = {
      kind: 'splitWord',
      separatorIndex: index,
    }
  },
})

function toggle(index: number) {
  separatorIndex.value = separatorIndex.value === index ? null : index
}
</script>

<template>
  <span data-cy="splitWordInput" class="main" :class="{ tricolorable }">
    <template v-for="(letter, index) in letters" :key="index">
      <span v-if="index > 0" class="inter">
        <span @click="toggle(index)">
          <template v-if="separatorIndex === index">{{ separator }}</template>
        </span>
      </span>
      <span class="letter">{{ letter }}</span>
    </template>
  </span>
</template>

<style scoped>
.main {
  line-height: 1em; /* Fix caret position on Chrome */
  padding: 4px calc(4px + var(--optional-extra-horizontal-space-between-letters-in-editable-text-input));
  border: 2px outset black;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
  white-space: nowrap;
}

.inter {
  cursor: pointer;
  display: inline-block;
  width: var(--optional-extra-horizontal-space-between-letters-in-editable-text-input);
  height: calc(1em + 4px);
  vertical-align: text-top;
}

.inter > span {
  display: inline-block;
  width: calc(100% + 6px);
  height: 100%;
  transform: translateX(-3px);
  text-align: center;
  color: #777;
}
</style>
