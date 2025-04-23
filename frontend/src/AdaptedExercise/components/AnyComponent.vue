<script setup lang="ts">
import type { Component } from '@/apiClient'
import ArrowComponent from './ArrowComponent.vue'
import FormattedComponent from './FormattedComponent.vue'
import FreeTextInput from './FreeTextInput.vue'
import MultipleChoicesInput from './MultipleChoicesInput.vue'
import SelectableInput from './SelectableInput.vue'
import SwappableInput from './SwappableInput.vue'
import TextComponent from './TextComponent.vue'
import WhitespaceComponent from './WhitespaceComponent.vue'
import { type ModelRef } from 'vue'

defineProps<{
  component: Component
  tricolorable: boolean
}>()

const model = defineModel<string | number | boolean>()
const modelAsString = model as ModelRef<string>
const modelAsNumber = model as ModelRef<number>
const modelAsBoolean = model as ModelRef<boolean>
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
  <SwappableInput
    v-else-if="component.kind === 'swappableInput'"
    v-bind="component"
    v-model="modelAsBoolean"
    :tricolorable
  />
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
