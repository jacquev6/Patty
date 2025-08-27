<script setup lang="ts">
import { h, type VNode } from 'vue'

import type { AnyRenderable } from '../AdaptedExerciseRenderer.vue'
import PassiveSingleComponent from './PassiveSingleComponent.vue'
import TextInputRenderer from '../components/TextInputRenderer.vue'
import MultipleChoicesInputRenderer from '../components/MultipleChoicesInputRenderer.vue'
import SelectableInputRenderer from '../components/SelectableInputRenderer.vue'
import SwappableInputRenderer from '../components/SwappableInputRenderer.vue'
import SplitWordInputRenderer from '../components/SplitWordInputRenderer.vue'
import { match, P } from 'ts-pattern'

const props = defineProps<{
  aloneOnLine: boolean
  component: AnyRenderable
  tricolorable: boolean
}>()

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: P.union('formatted', 'text', 'whitespace') }, (c) =>
      h(PassiveSingleComponent, {
        component: c,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'textInput' }, ({ path, initialText, increaseHorizontalSpace }) =>
      h(TextInputRenderer, {
        path,
        initialText,
        increaseHorizontalSpace,
        tricolorable: props.tricolorable,
        aloneOnLine: props.aloneOnLine,
      }),
    )
    .with({ kind: 'multipleChoicesInput' }, ({ path, choices, showChoicesByDefault }) =>
      h(MultipleChoicesInputRenderer, {
        path,
        choices,
        showChoicesByDefault,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'selectableInput' }, ({ path, contents, colors, boxed, mayBeSingleLetter }) =>
      h(SelectableInputRenderer, {
        path,
        contents,
        colors,
        boxed,
        mayBeSingleLetter,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'swappableInput' }, ({ path, contents }) =>
      h(SwappableInputRenderer, {
        path,
        contents,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'splitWordInput' }, ({ path, word }) =>
      h(SplitWordInputRenderer, {
        path,
        word,
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
