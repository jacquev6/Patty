<script setup lang="ts">
import { computed } from 'vue'

import type { Component } from '@/apiClient'
import FormattedComponent from './FormattedComponent.vue'

const props = defineProps<{
  kind: 'selectableInput'
  contents: Component[]
  colors: string[]
  tricolorable: boolean
}>()

const colorIndex = defineModel<number>({ default: 0 })

function increment() {
  colorIndex.value = (colorIndex.value + 1) % (props.colors.length + 1)
}

const contents = computed(() => ({
  kind: 'formatted' as const,
  contents: props.contents,
  bold: false,
  italic: false,
  highlighted: colorIndex.value === 0 ? null : props.colors[colorIndex.value - 1],
  boxed: false,
}))
</script>

<template>
  <FormattedComponent class="main" v-bind="contents" :tricolorable data-cy="selectableInput" @click="increment()" />
</template>

<style scoped>
.main {
  cursor: pointer;
}
</style>
