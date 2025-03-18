<script setup lang="ts">
import type { Component } from '@/apiClient'
import ArrowComponent from './ArrowComponent.vue'
import FreeTextInput from './FreeTextInput.vue'
import MultipleChoicesInput from './MultipleChoicesInput.vue'
import SelectableInput from './SelectableInput.vue'
import SequenceComponent from './SequenceComponent.vue'
import TextComponent from './TextComponent.vue'
import WhitespaceComponent from './WhitespaceComponent.vue'

defineProps<{
  component: Component
}>()
</script>

<template>
  <ArrowComponent v-if="component.kind === 'arrow'" v-bind="component" />
  <FreeTextInput v-else-if="component.kind === 'freeTextInput'" v-bind="component" />
  <MultipleChoicesInput v-else-if="component.kind === 'multipleChoicesInput'" v-bind="component" />
  <SelectableInput v-else-if="component.kind === 'selectableInput'" v-bind="component" />
  <SequenceComponent v-else-if="component.kind === 'sequence'" v-bind="component" />
  <TextComponent v-else-if="component.kind === 'text'" v-bind="component" />
  <WhitespaceComponent v-else-if="component.kind === 'whitespace'" v-bind="component" />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
