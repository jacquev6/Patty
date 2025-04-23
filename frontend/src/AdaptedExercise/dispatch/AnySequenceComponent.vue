<script setup lang="ts">
import type { AnyComponent } from '@/apiClient'
import AnySingleComponent from './AnySingleComponent.vue'

const props = defineProps<{
  contents: AnyComponent[]
  tricolorable: boolean
}>()

const model = defineModel<Record<number, undefined | string | number | null | boolean>>({ required: true })
</script>

<template>
  <AnySingleComponent
    v-for="(component, componentIndex) in props.contents"
    :component
    :tricolorable
    v-model="model[componentIndex]"
  />
</template>
