<script setup lang="ts">
import { computed } from 'vue'

import type { Component } from '@/apiClient'
import LineComponent from './LineComponent.vue'

const props = defineProps<{
  kind: 'sequence'
  contents: Component[]
  bold: boolean
  italic: boolean
  highlighted: string | null
  boxed: boolean
  tricolorable: boolean
}>()

const style = computed(() => ({
  backgroundColor: props.highlighted ?? undefined,
  fontWeight: props.bold ? 'bold' : undefined,
  fontStyle: props.italic ? 'italic' : undefined,
  border: props.boxed ? '2px solid black' : undefined,
  padding: props.boxed ? '4px' : undefined,
}))
</script>

<template>
  <span :style><LineComponent :contents :tricolorable /></span>
</template>
