<script setup lang="ts">
import { computed } from 'vue'

import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import PassiveSequenceComponent from '../dispatch/PassiveSequenceComponent.vue'

const props = defineProps<{
  contents: PassiveRenderable[]
  bold: boolean
  italic: boolean
  underlined: boolean
  highlighted: string | null
  boxed: boolean
  subscript: boolean
  superscript: boolean
  tricolorable: boolean
}>()

const style = computed(() => ({
  backgroundColor: props.highlighted ?? undefined,
  fontWeight: props.bold ? 'bold' : undefined,
  fontStyle: props.italic ? 'italic' : undefined,
  border: props.boxed ? '2px solid black' : undefined,
  padding: props.boxed ? '4px' : undefined,
  textDecorationLine: props.underlined ? 'underline' : undefined,
  verticalAlign: props.subscript ? 'sub' : props.superscript ? 'super' : undefined,
  fontSize: props.subscript || props.superscript ? '0.8em' : undefined,
}))
</script>

<template>
  <span :style><PassiveSequenceComponent :contents :tricolorable /></span>
</template>
