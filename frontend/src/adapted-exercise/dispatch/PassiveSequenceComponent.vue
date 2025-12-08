<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import type { PassiveRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import PassiveSingleComponent from './PassiveSingleComponent.vue'

const props = defineProps<{
  contents: PassiveRenderable[]
  tricolorable: boolean
}>()
</script>

<template>
  <PassiveSingleComponent v-for="component in props.contents" :component :tricolorable />
</template>
