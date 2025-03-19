<script setup lang="ts">
import { computed } from 'vue'

import type { Line } from '@/apiClient'
import SequenceComponent from './SequenceComponent.vue'

const props = defineProps<{
  kind: 'selectableInput'
  contents: Line
  colors: string[]
  tricolorable: boolean
}>()

const colorIndex = defineModel<number>({ default: 0 })

function increment() {
  colorIndex.value = (colorIndex.value + 1) % (props.colors.length + 1)
}

const contents = computed(() => ({
  kind: 'sequence' as const,
  contents: props.contents.contents,
  bold: false,
  italic: false,
  highlighted: colorIndex.value === 0 ? null : props.colors[colorIndex.value - 1],
  boxed: false,
  vertical: false,
}))
</script>

<template>
  <SequenceComponent class="main" v-bind="contents" :tricolorable data-cy="selectableInput" @click="increment()" />
</template>

<style scoped>
.main {
  cursor: pointer;
}
</style>
