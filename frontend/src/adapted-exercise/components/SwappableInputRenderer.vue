<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, inject, nextTick, ref, useTemplateRef, type Ref } from 'vue'

import assert from '$/assert'
import type { PassiveRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import FormattedTextRenderer from './FormattedTextRenderer.vue'
import TextInputRenderer from './TextInputRenderer.vue'
import type { InProgressExercise, StudentAnswers } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'

const props = defineProps<{
  path: string
  contents: PassiveRenderable[]
  editable: boolean
  tricolorable: boolean
}>()

const studentAnswers = inject<Ref<StudentAnswers>>('adaptedExerciseStudentAnswers')
assert(studentAnswers !== undefined)

const inProgress = inject<InProgressExercise>('adaptedExerciseInProgress')
assert(inProgress !== undefined)

const selected = computed(() => inProgress.p.kind === 'movingSwappable' && inProgress.p.swappable.path === props.path)

const contentsFrom = computed(() => {
  const answer = studentAnswers.value[`${props.path}-swp`]
  if (answer === undefined) {
    return props.path
  } else {
    assert(answer.kind === 'swappable')
    return answer.contentsFrom
  }
})

const actualContents = computed(() => {
  const answer = studentAnswers.value[`${contentsFrom.value}-txt`]
  if (answer === undefined) {
    return inProgress.swappables[contentsFrom.value].contents
  } else {
    assert(answer.kind === 'text')
    return [{ kind: 'text' as const, text: answer.text }]
  }
})

const highlighted = computed(() => (selected.value ? '#FFFDD4' : null))

function setAnswer(path: string, contentsFrom: string) {
  assert(studentAnswers !== undefined)
  studentAnswers.value[path] = { kind: 'swappable', contentsFrom }
}

function handleClick() {
  assert(inProgress !== undefined)
  if (inProgress.p.kind === 'movingSwappable') {
    if (inProgress.p.swappable.path !== props.path) {
      const contentsFromBefore = contentsFrom.value
      setAnswer(`${props.path}-swp`, inProgress.p.swappable.contentsFrom)
      setAnswer(`${inProgress.p.swappable.path}-swp`, contentsFromBefore)
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

const textInput = useTemplateRef('textInput')
const editing = ref(false)
const contentBeingEdited = ref('')

const tricolorablesTriggerRecoloring = inject<Ref<number>>('tricolorablesTriggerRecoloring')
assert(tricolorablesTriggerRecoloring !== undefined)

async function handleDoubleClick() {
  assert(inProgress !== undefined)
  if (props.editable) {
    inProgress.p = { kind: 'none' }
    contentBeingEdited.value = actualContents.value
      .map((c) => {
        if (c.kind === 'text') {
          return c.text
        } else {
          assert(c.kind === 'whitespace')
          return ' '
        }
      })
      .join('')
    editing.value = true
    await nextTick()
    assert(textInput.value !== null)
    textInput.value.focus()
    assert(tricolorablesTriggerRecoloring !== undefined)
    tricolorablesTriggerRecoloring.value += 1
  }
}

function handleBlur() {
  editing.value = false
  assert(tricolorablesTriggerRecoloring !== undefined)
  tricolorablesTriggerRecoloring.value += 1
}
</script>

<template>
  <TextInputRenderer
    v-if="editing"
    ref="textInput"
    :path="`${contentsFrom}-txt`"
    :initialText="contentBeingEdited"
    :increaseHorizontalSpace="false"
    :aloneOnLine="false"
    :tricolorable
    @blur="handleBlur"
  />
  <FormattedTextRenderer
    v-else
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
    @dblclick="handleDoubleClick"
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
