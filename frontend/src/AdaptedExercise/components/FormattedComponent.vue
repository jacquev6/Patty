<script setup lang="ts">
import { computed } from 'vue'

import type { PassiveComponent } from '@/apiClient'
import PassiveSequenceComponent from '../dispatch/PassiveSequenceComponent.vue'

const props = defineProps<{
  kind: 'formatted'
  contents: PassiveComponent[]
  bold: boolean
  italic: boolean
  underlined: boolean
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
  textDecorationLine: props.underlined ? 'underline' : undefined,
}))
</script>

<template>
  <span :style><PassiveSequenceComponent :contents :tricolorable /></span>
</template>
