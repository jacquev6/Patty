<script setup lang="ts">
import type { Component } from '@/apiClient'
import AnyComponent from './AnyComponent.vue'

const props = defineProps<{
  contents: Component[]
}>()

const model = defineModel<Record<number, string | number>>({ default: [] })
</script>

<template>
  <AnyComponent v-for="(component, componentIndex) in props.contents" :component v-model="model[componentIndex]" />
</template>
