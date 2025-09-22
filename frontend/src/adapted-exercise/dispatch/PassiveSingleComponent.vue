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
    .with({ kind: 'image' }, ({ url }) => h(ImageRenderer, { url }))
    .exhaustive()
}
</script>

<!-- This is awkward; I'm sure there is a way to define this component without a template -->
<template>
  <render />
</template>
