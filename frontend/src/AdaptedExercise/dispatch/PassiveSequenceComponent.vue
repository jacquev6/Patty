<script setup lang="ts">
import type { PassiveRenderable } from '../AdaptedExerciseRenderer.vue'
import PassiveSingleComponent from './PassiveSingleComponent.vue'

const props = defineProps<{
  contents: PassiveRenderable[]
  tricolorable: boolean
}>()
</script>

<template>
  <PassiveSingleComponent v-for="component in props.contents" :component :tricolorable />
</template>
