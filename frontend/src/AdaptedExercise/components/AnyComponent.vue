<script setup lang="ts">
import type { Component } from '@/apiClient'
import ArrowComponent from './ArrowComponent.vue'
import FreeTextInput from './FreeTextInput.vue'
import MultipleChoicesInput from './MultipleChoicesInput.vue'
import SelectableInput from './SelectableInput.vue'
import SequenceComponent from './SequenceComponent.vue'
import TextComponent from './TextComponent.vue'
import WhitespaceComponent from './WhitespaceComponent.vue'
import { type ModelRef } from 'vue'

defineProps<{
  component: Component
  tricolorable: boolean
}>()

const model = defineModel<string | number>()
const modelAsString = model as ModelRef<string>
const modelAsNumber = model as ModelRef<number>
</script>

<template>
  <ArrowComponent v-if="component.kind === 'arrow'" v-bind="component" :tricolorable />
  <FreeTextInput
    v-else-if="component.kind === 'freeTextInput'"
    v-bind="component"
    v-model="modelAsString"
    :tricolorable
  />
  <MultipleChoicesInput
    v-else-if="component.kind === 'multipleChoicesInput'"
    v-bind="component"
    v-model="modelAsNumber"
    :tricolorable
  />
  <SelectableInput
    v-else-if="component.kind === 'selectableInput'"
    v-bind="component"
    v-model="modelAsNumber"
    :tricolorable
  />
  <SequenceComponent v-else-if="component.kind === 'sequence'" v-bind="component" :tricolorable />
  <TextComponent v-else-if="component.kind === 'text'" v-bind="component" :tricolorable />
  <WhitespaceComponent v-else-if="component.kind === 'whitespace'" v-bind="component" />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
