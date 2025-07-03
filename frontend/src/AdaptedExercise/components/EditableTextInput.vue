<script setup lang="ts">
import { computed } from 'vue'

import assert from '@/assert'
import type { PlainText } from '@/apiClient'
import type { StudentAnswers } from '../AdaptedExerciseRenderer.vue'
import FreeTextInput from './FreeTextInput.vue'
import { match, P } from 'ts-pattern'

const props = defineProps<{
  kind: 'editableTextInput'
  pageIndex: number
  lineIndex: number
  componentIndex: number
  contents: PlainText[]
  showOriginalText: false
  tricolorable: boolean
  aloneOnLine: boolean
}>()

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const initialText = computed(() =>
  props.contents
    .map((c) =>
      match(c)
        .returnType<string>()
        .with({ kind: 'text', text: P.select() }, (text) => text)
        .with({ kind: 'whitespace' }, () => ' ')
        .exhaustive(),
    )
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
  <FreeTextInput kind="freeTextInput" v-model="modelProxy" :tricolorable :aloneOnLine />
</template>
