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
import { match } from 'ts-pattern'

import type { PassiveRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import FormattedRenderer from '@/adapted-exercise/components/FormattedTextRenderer.vue'
import TextRenderer from '@/adapted-exercise/components/TextRenderer.vue'
import WhitespaceRenderer from '@/adapted-exercise/components/WhitespaceRenderer.vue'
import ImageRenderer from '@/adapted-exercise/components/ImageRenderer.vue'

const props = defineProps<{
  component: PassiveRenderable
  tricolorable: boolean
}>()

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: 'text' }, ({ text }) => h(TextRenderer, { text, tricolorable: props.tricolorable }))
    .with({ kind: 'whitespace' }, () => h(WhitespaceRenderer))
    .with({ kind: 'formatted' }, ({ contents, bold, boxed, highlighted, italic, subscript, superscript, underlined }) =>
      h(FormattedRenderer, {
        contents,
        bold,
        boxed,
        highlighted,
        italic,
        subscript,
        superscript,
        underlined,
        tricolorable: props.tricolorable,
      }),
    )
    .with({ kind: 'image' }, ({ url, height }) => h(ImageRenderer, { url, height }))
    .exhaustive()
}
</script>

<!-- This is awkward; I'm sure there is a way to define this component without a template -->
<template>
  <render />
</template>
