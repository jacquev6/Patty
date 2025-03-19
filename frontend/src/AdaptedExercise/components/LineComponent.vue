<script setup lang="ts">
import type { Component } from '@/apiClient'
import AnyComponent from './AnyComponent.vue'

const props = defineProps<{
  contents: Component[]
  tricolorable: boolean
}>()

const model = defineModel<Record<number, string | number>>({ default: [] })
</script>

<template>
  <AnyComponent
    v-for="(component, componentIndex) in props.contents"
    :component
    :tricolorable
    v-model="model[componentIndex]"
  />
</template>
