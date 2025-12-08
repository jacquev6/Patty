<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed } from 'vue'

import type { AnyRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import AnySequenceComponent from '@/adapted-exercise/dispatch/AnySequenceComponent.vue'

const props = defineProps<{
  contents: AnyRenderable[]
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
  <span :style><AnySequenceComponent :contents :tricolorable /></span>
</template>
