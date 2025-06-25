<script setup lang="ts">
import { h, type VNode } from 'vue'
import { match } from 'ts-pattern'

import type { PassiveComponent } from '@/apiClient'
import ArrowComponent from '../components/ArrowComponent.vue'
import FormattedComponent from '../components/FormattedComponent.vue'
import TextComponent from '../components/TextComponent.vue'
import WhitespaceComponent from '../components/WhitespaceComponent.vue'

const props = defineProps<{
  component: PassiveComponent
  tricolorable: boolean
}>()

function render() {
  return match(props.component)
    .returnType<VNode>()
    .with({ kind: 'arrow' }, (c) => h(ArrowComponent, { ...c, tricolorable: props.tricolorable }))
    .with({ kind: 'choice' }, (c) =>
      h(FormattedComponent, { ...c, kind: 'formatted', boxed: true, tricolorable: props.tricolorable }),
    )
    .with({ kind: 'text' }, (c) => h(TextComponent, { ...c, tricolorable: props.tricolorable }))
    .with({ kind: 'whitespace' }, (c) => h(WhitespaceComponent, c))
    .with({ kind: 'formatted' }, (c) => h(FormattedComponent, { ...c, tricolorable: props.tricolorable }))
    .exhaustive()
}
</script>

<!-- This is awkward; I'm sure there is a way to define this component without a template -->
<template>
  <render />
</template>
