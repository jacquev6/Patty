<script setup lang="ts">
import { computed } from 'vue'

import type { AnyComponent } from '@/apiClient'
import assert from '@/assert'
import PassiveSingleComponent, { isPassive } from './PassiveSingleComponent.vue'
import FreeTextInput from '../components/FreeTextInput.vue'
import MultipleChoicesInput from '../components/MultipleChoicesInput.vue'
import SelectableInput from '../components/SelectableInput.vue'
import SwappableInput from '../components/SwappableInput.vue'

defineProps<{
  component: AnyComponent
  tricolorable: boolean
}>()

const model = defineModel<undefined | string | number | null | boolean>({ required: true })

const modelForFreeTextInput = computed<string>({
  get() {
    if (model.value === undefined) {
      return ''
    } else {
      assert(typeof model.value === 'string')
      return model.value
    }
  },
  set: (value: string) => {
    model.value = value
  },
})

const modelForMultipleChoicesInput = computed<number | null, number | null>({
  get() {
    if (model.value === undefined) {
      return null
    } else {
      assert(model.value === null || typeof model.value === 'number')
      return model.value
    }
  },
  set: (value: number | null) => {
    model.value = value
  },
})

const modelForSelectableInput = computed<number, number>({
  get() {
    if (model.value === undefined) {
      return 0
    } else {
      assert(typeof model.value === 'number')
      return model.value
    }
  },
  set: (value: number) => {
    model.value = value
  },
})

const modelForSwappableInput = computed<boolean, boolean>({
  get() {
    if (model.value === undefined) {
      return false
    } else {
      assert(typeof model.value === 'boolean')
      return model.value
    }
  },
  set: (value: boolean) => {
    model.value = value
  },
})
</script>

<template>
  <PassiveSingleComponent v-if="isPassive(component)" :component="component" :tricolorable="tricolorable" />
  <FreeTextInput
    v-else-if="component.kind === 'freeTextInput'"
    v-bind="component"
    v-model="modelForFreeTextInput"
    :tricolorable
  />
  <MultipleChoicesInput
    v-else-if="component.kind === 'multipleChoicesInput'"
    v-bind="component"
    v-model="modelForMultipleChoicesInput"
    :tricolorable
  />
  <SelectableInput
    v-else-if="component.kind === 'selectableInput'"
    v-bind="component"
    v-model="modelForSelectableInput"
    :tricolorable
  />
  <SwappableInput
    v-else-if="component.kind === 'swappableInput'"
    v-bind="component"
    v-model="modelForSwappableInput"
    :tricolorable
  />
  <template v-else>BUG (component not handled): {{ ((contents: never) => contents)(component) }}</template>
</template>
