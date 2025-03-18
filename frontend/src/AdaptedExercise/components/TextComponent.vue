<script setup lang="ts">
defineProps<{
  kind: 'text'
  text: string
}>()
</script>

<template>
  <span>{{ text }}</span>
</template>
