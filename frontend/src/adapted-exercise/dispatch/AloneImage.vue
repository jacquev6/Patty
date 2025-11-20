<script setup lang="ts">
import type { ImageRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import ImageRenderer from '@/adapted-exercise/components/ImageRenderer.vue'

const props = defineProps<{
  component: ImageRenderable
}>()
</script>

<template>
  <p :style="{ textAlign: props.component.align }"><ImageRenderer :url="component.url" :height="component.height" /></p>
</template>
