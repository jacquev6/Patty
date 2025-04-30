<script lang="ts">
import type { PassiveComponent, AnyComponent } from '@/apiClient'

export function isPassive(component: AnyComponent): component is PassiveComponent {
  return (
    component.kind === 'arrow' ||
    component.kind === 'choice' ||
    component.kind === 'formatted' ||
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
    :contents="component.contents"
    :bold="false"
    :italic="false"
    :underlined="false"
    :highlighted="null"
    :boxed="true"
    :tricolorable
  />
  <TextComponent v-else-if="component.kind === 'text'" v-bind="component" :tricolorable />
  <WhitespaceComponent v-else-if="component.kind === 'whitespace'" v-bind="component" />
  <FormattedComponent v-else-if="component.kind === 'formatted'" v-bind="component" :tricolorable />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
