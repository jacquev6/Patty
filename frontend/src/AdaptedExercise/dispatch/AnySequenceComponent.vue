<script setup lang="ts">
import type { AnyRenderable } from '../AdaptedExerciseRenderer.vue'
import AnySingleComponent from './AnySingleComponent.vue'

const props = defineProps<{
  contents: AnyRenderable[]
  aloneOnLine: boolean
  tricolorable: boolean
}>()
</script>

<template>
  <AnySingleComponent v-for="component in props.contents" :aloneOnLine :component :tricolorable />
</template>
