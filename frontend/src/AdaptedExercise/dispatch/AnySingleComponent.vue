<script setup lang="ts">
import { h, type VNode } from 'vue'

import type { AnyRenderable } from '../AdaptedExerciseRenderer.vue'
import PassiveSingleComponent from './PassiveSingleComponent.vue'
import TextInputRenderer from '../components/TextInputRenderer.vue'
import MultipleChoicesInputRenderer from '../components/MultipleChoicesInputRenderer.vue'
import SelectableInputRenderer from '../components/SelectableInputRenderer.vue'
import SwappableInputRenderer from '../components/SwappableInputRenderer.vue'
import type { StudentAnswers, ComponentAnswer, InProgressExercise } from '../AdaptedExerciseRenderer.vue'
import { match, P } from 'ts-pattern'
import SelectableLettersInputRenderer from '../components/SelectableLettersInputRenderer.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  aloneOnLine: boolean
  componentIndex: number
  component: AnyRenderable
  tricolorable: boolean
}>()

const studentAnswers = defineModel<StudentAnswers>({ required: true })

const inProgress = defineModel<InProgressExercise>('inProgress', { required: true })

function getComponentAnswer() {
  return studentAnswers.value.pages[props.pageIndex]?.lines?.[props.lineIndex]?.components[props.componentIndex]
}

function setComponentAnswer(answer: ComponentAnswer) {
  studentAnswers.value.pages[props.pageIndex] ??= { lines: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex] ??= { components: {} }
  studentAnswers.value.pages[props.pageIndex]!.lines[props.lineIndex]!.components[props.componentIndex] = answer
}

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: P.union('formatted', 'text', 'whitespace') }, (c) =>
      h(PassiveSingleComponent, {
        component: c,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'textInput' }, ({ initialText, increaseHorizontalSpace }) =>
      h(TextInputRenderer, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        initialText,
        increaseHorizontalSpace,
        tricolorable: props.tricolorable,
        aloneOnLine: props.aloneOnLine,
        getComponentAnswer,
        setComponentAnswer,
      }),
    )
    .with({ kind: 'multipleChoicesInput' }, ({ choices, showChoicesByDefault }) =>
      h(MultipleChoicesInputRenderer, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        choices,
        showChoicesByDefault,
        tricolorable: props.tricolorable,
        inProgress: inProgress.value,
        'onUpdate:inProgress': (v) => {
          inProgress.value = v
        },
        getComponentAnswer,
        setComponentAnswer,
      }),
    )
    .with({ kind: 'selectableInput' }, ({ contents, colors, boxed }) =>
      h(SelectableInputRenderer, {
        contents,
        colors,
        boxed,
        tricolorable: props.tricolorable,
        getComponentAnswer,
        setComponentAnswer,
      }),
    )
    .with({ kind: 'selectableLettersInput' }, ({ contents, colors, boxed }) =>
      h(SelectableLettersInputRenderer, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        contents,
        colors,
        boxed,
        tricolorable: props.tricolorable,
        inProgress: inProgress.value,
        'onUpdate:inProgress': (v) => {
          inProgress.value = v
        },
        getComponentAnswer,
        setComponentAnswer,
      }),
    )
    .with({ kind: 'swappableInput' }, ({ contents }) =>
      h(SwappableInputRenderer, {
        pageIndex: props.pageIndex,
        lineIndex: props.lineIndex,
        componentIndex: props.componentIndex,
        contents,
        inProgress: inProgress.value,
        'onUpdate:inProgress': (v) => {
          inProgress.value = v
        },
        modelValue: studentAnswers.value,
        'onUpdate:modelValue': (v) => {
          studentAnswers.value = v
        },
        tricolorable: props.tricolorable,
      }),
    )
    .exhaustive()
}
</script>

<!-- This is awkward; I'm sure there is a way to define this component without a template -->
<template>
  <render />
</template>
