<script setup lang="ts">
import { computed } from 'vue'

import assert from '@/assert'
import type { PlainText } from '@/apiClient'
import type { StudentAnswers } from '../AdaptedExerciseRenderer.vue'
import FreeTextInput from './FreeTextInput.vue'

const props = defineProps<{
  kind: 'activeEditableTextInput'
  pageIndex: number
  lineIndex: number
  componentIndex: number
  contents: PlainText[]
  tricolorable: boolean
}>()

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const initialText = computed(() =>
  props.contents
    .map((c) => {
      if (c.kind === 'text') {
        return c.text
      } else if (c.kind === 'whitespace') {
        return ' '
      } else {
        ;((c: never) => console.log('Unknown content', c))(c)
      }
    })
    .join(''),
)

const modelProxy = computed<string>({
  get() {
    const answer = studentAnswers.value.pages[props.pageIndex]?.lines[props.lineIndex]?.components[props.componentIndex]
    if (answer === undefined) {
      return initialText.value
    } else {
      assert(answer.kind === 'editableTextInput')
      return answer.text
    }
  },
  set(value: string) {
    studentAnswers.value.pages[props.pageIndex] ??= { lines: {} }
    studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex] ??= { components: {} }
    studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex]!.components[props.componentIndex] = {
      kind: 'editableTextInput',
      text: value,
    }
  },
})
</script>

<template>
  <FreeTextInput kind="freeTextInput" v-model="modelProxy" :tricolorable />
</template>
