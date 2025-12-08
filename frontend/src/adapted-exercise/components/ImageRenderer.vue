<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
defineProps<{
  url: string
  height: string
}>()
</script>

<template>
  <img :src="url" :style="{ height }" />
</template>

<style scoped>
img {
  vertical-align: middle;
  margin: 0.5em;
}
</style>
