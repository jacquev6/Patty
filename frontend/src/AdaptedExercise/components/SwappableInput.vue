<script setup lang="ts">
import { computed } from 'vue'

import type { PassiveComponent } from '@/apiClient'
import FormattedComponent from './FormattedComponent.vue'

const props = defineProps<{
  kind: 'swappableInput'
  contents: PassiveComponent[]
  tricolorable: boolean
}>()

const selected = defineModel<boolean>({ required: true })

const contents = computed(() => ({
  kind: 'formatted' as const,
  contents: props.contents,
  bold: false,
  italic: false,
  highlighted: selected.value ? '#FFFDD4' : null,
  boxed: false,
}))
</script>

<template>
  <FormattedComponent
    class="main"
    v-bind="contents"
    :tricolorable
    data-cy="swappableInput"
    @click="selected = !selected"
  />
</template>

<style scoped>
.main {
  cursor: pointer;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
  border: 2px solid #aaf;
  padding: 0.2em 0.5em;
}
</style>
