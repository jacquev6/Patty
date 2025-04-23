<script lang="ts">
import type { PassiveComponent, AnyComponent } from '@/apiClient'

export function isPassive(component: AnyComponent): component is PassiveComponent {
  return (
    component.kind === 'arrow' ||
    component.kind === 'choice' ||
    component.kind === 'text' ||
    component.kind === 'whitespace'
  )
}
</script>

<script setup lang="ts">
import ArrowComponent from '../components/ArrowComponent.vue'
import FormattedComponent from '../components/FormattedComponent.vue'
import TextComponent from '../components/TextComponent.vue'
import WhitespaceComponent from '../components/WhitespaceComponent.vue'

defineProps<{
  component: PassiveComponent
  tricolorable: boolean
}>()
</script>

<template>
  <ArrowComponent v-if="component.kind === 'arrow'" v-bind="component" :tricolorable />
  <FormattedComponent
    v-else-if="component.kind === 'choice'"
    kind="formatted"
    :bold="false"
    :boxed="true"
    :contents="component.contents"
    :highlighted="null"
    :italic="false"
    :tricolorable
  />
  <TextComponent v-else-if="component.kind === 'text'" v-bind="component" :tricolorable />
  <WhitespaceComponent v-else-if="component.kind === 'whitespace'" v-bind="component" />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
