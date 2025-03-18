<script setup lang="ts">
import type { Component } from '@/apiClient'
import AnyComponent from './AnyComponent.vue'

const props = defineProps<{
  contents: Component[]
}>()
</script>

<template>
  <AnyComponent v-for="component in props.contents" :component />
</template>
