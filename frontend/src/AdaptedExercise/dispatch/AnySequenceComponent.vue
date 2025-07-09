<script setup lang="ts">
import type { AnyRenderable } from '../AdaptedExerciseRenderer.vue'
import AnySingleComponent from './AnySingleComponent.vue'

const props = defineProps<{
  pageIndex: number
  lineIndex: number
  contents: AnyRenderable[]
  aloneOnLine: boolean
  tricolorable: boolean
}>()
</script>

<template>
  <AnySingleComponent
    v-for="(component, componentIndex) in props.contents"
    :pageIndex
    :lineIndex
    :aloneOnLine
    :componentIndex
    :component
    :tricolorable
  />
</template>
