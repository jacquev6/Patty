<script setup lang="ts">
import type { AnyRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import AnySingleComponent from './AnySingleComponent.vue'

const props = defineProps<{
  contents: AnyRenderable[]
  tricolorable: boolean
}>()
</script>

<template>
  <AnySingleComponent v-for="component in props.contents" :aloneOnLine="false" :component :tricolorable />
</template>
