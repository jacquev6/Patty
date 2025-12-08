<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
const emit = defineEmits<{
  (e: 'click'): void
}>()
</script>

<template>
  <span data-cy="virtual-button" @pointerdown.prevent="emit('click')"><slot></slot></span>
</template>

<style scoped>
span {
  padding: 4px 8px;
  border: 2px black outset;
  cursor: pointer;
}
</style>
