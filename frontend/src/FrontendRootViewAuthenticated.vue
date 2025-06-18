<script setup lang="ts">
import { useApiConstantsStore } from './ApiConstantsStore'

const apiConstantsStore = useApiConstantsStore()
</script>

<template>
  <RouterView v-if="apiConstantsStore.ready" />
</template>
