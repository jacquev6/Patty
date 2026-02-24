<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { h, type VNode } from 'vue'

import type { AnyRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import PassiveSingleComponent from './PassiveSingleComponent.vue'
import TextInputRenderer from '@/adapted-exercise/components/TextInputRenderer.vue'
import MultipleChoicesInputRenderer from '@/adapted-exercise/components/MultipleChoicesInputRenderer.vue'
import SelectableInputRenderer from '@/adapted-exercise/components/SelectableInputRenderer.vue'
import SwappableInputRenderer from '@/adapted-exercise/components/SwappableInputRenderer.vue'
import SplitWordInputRenderer from '@/adapted-exercise/components/SplitWordInputRenderer.vue'
import { match, P } from 'ts-pattern'

const props = defineProps<{
  aloneOnLine: boolean
  component: AnyRenderable
  tricolorable: boolean
}>()

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: P.union('formatted', 'text', 'whitespace', 'image') }, (c) =>
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
    .with({ kind: 'multipleChoicesInput' }, ({ path, choices, showChoicesByDefault, reducedLineSpacing }) =>
      h(MultipleChoicesInputRenderer, {
        path,
        choices,
        showChoicesByDefault,
        reducedLineSpacing,
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
    .with({ kind: 'swappableInput' }, ({ path, contents, editable }) =>
      h(SwappableInputRenderer, {
        path,
        contents,
        editable,
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
