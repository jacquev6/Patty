<script setup lang="ts">
defineProps<{
  kind: 'whitespace'
}>()

const whitespace = ' '
</script>

<template>
  <span>{{ whitespace }}</span>
</template>
