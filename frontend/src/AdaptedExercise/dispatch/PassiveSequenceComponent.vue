<script setup lang="ts">
import type { PassiveComponent } from '@/apiClient'
import PassiveSingleComponent from './PassiveSingleComponent.vue'

const props = defineProps<{
  contents: PassiveComponent[]
  tricolorable: boolean
}>()
</script>

<template>
  <PassiveSingleComponent v-for="component in props.contents" :component :tricolorable />
</template>
