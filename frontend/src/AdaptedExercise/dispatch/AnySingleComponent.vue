<script setup lang="ts">
import { computed, h, type Ref, type VNode } from 'vue'

import type { AnyComponent } from '@/apiClient'
import assert from '@/assert'
import PassiveSingleComponent from './PassiveSingleComponent.vue'
import FreeTextInput from '../components/FreeTextInput.vue'
import MultipleChoicesInput from '../components/MultipleChoicesInput.vue'
import SelectableInput from '../components/SelectableInput.vue'
import SwappableInput from '../components/SwappableInput.vue'
import type { StudentAnswers, ComponentAnswer, InProgressExercise } from '../AdaptedExerciseRenderer.vue'
import PassiveSequenceComponent from './PassiveSequenceComponent.vue'
import EditableTextInput from '../components/EditableTextInput.vue'
import { match, P } from 'ts-pattern'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  aloneOnLine: boolean
  componentIndex: number
  component: AnyComponent
  tricolorable: boolean
}>()

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const inProgress = defineModel<InProgressExercise>('inProgress', { required: true })

function getComponentAnswer() {
  return studentAnswers.value.pages[props.pageIndex]?.lines[props.lineIndex]?.components[props.componentIndex]
}

function setComponentAnswer(answer: ComponentAnswer) {
  studentAnswers.value.pages[props.pageIndex] ??= { lines: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex] ??= { components: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex]!.components[props.componentIndex] = answer
}

const answerForFreeTextInput = computed<string>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return ''
    } else {
      assert(answer.kind === 'freeTextInput')
      return answer.text
    }
  },
  set: (text: string) => {
    setComponentAnswer({ kind: 'freeTextInput', text })
  },
})

const answerForMultipleChoicesInput = computed<number | null, number | null>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return null
    } else {
      assert(answer.kind === 'multipleChoicesInput')
      return answer.choice
    }
  },
  set: (choice: number | null) => {
    setComponentAnswer({ kind: 'multipleChoicesInput', choice })
  },
})

const answerForSelectableInput = computed<number, number>({
  get() {
    const answer = getComponentAnswer()
    if (answer === undefined) {
      return 0
    } else {
      assert(answer.kind === 'selectableInput')
      return answer.color
    }
  },
  set: (color: number) => {
    setComponentAnswer({ kind: 'selectableInput', color })
  },
})

function vModel<T>(r: Ref<T>) {
  return {
    modelValue: r.value,
    'onUpdate:modelValue': (v: T) => {
      r.value = v
    },
  }
}

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: P.union('arrow', 'choice', 'formatted', 'text', 'whitespace') }, (c) =>
      h(PassiveSingleComponent, {
        component: c,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'freeTextInput' }, (c) =>
      h(FreeTextInput, {
        ...c,
        ...vModel(answerForFreeTextInput),
        tricolorable: props.tricolorable,
        aloneOnLine: props.aloneOnLine,
      }),
    )
    .with({ kind: 'multipleChoicesInput' }, (c) =>
      h(MultipleChoicesInput, {
        ...c,
        ...vModel(answerForMultipleChoicesInput),
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'selectableInput' }, (c) =>
      h(SelectableInput, {
        ...c,
        ...vModel(answerForSelectableInput),
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'swappableInput' }, (c) =>
      h(SwappableInput, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        ...c,
        inProgress: inProgress.value,
        'onUpdate:inProgress': (v) => {
          inProgress.value = v
        },
        ...vModel(studentAnswers),
        tricolorable: props.tricolorable,
      }),
    )
    .with(
      { kind: 'editableTextInput' },
      (c) => c.showOriginalText,
      (c) =>
        h(PassiveSequenceComponent, {
          contents: c.contents,
          tricolorable: props.tricolorable,
        }),
    )
    .with({ kind: 'editableTextInput' }, (c) =>
      h(EditableTextInput, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        ...c,
        kind: 'editableTextInput',
        showOriginalText: false,
        ...vModel(studentAnswers),
        tricolorable: props.tricolorable,
        aloneOnLine: props.aloneOnLine,
      }),
    )
    .exhaustive()
}
</script>

<!-- This is awkward; I'm sure there is a way to define this component without a template -->
<template>
  <render />
</template>
